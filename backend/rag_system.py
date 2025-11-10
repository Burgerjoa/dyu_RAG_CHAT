"""
동양대학교 RAG 기반 챗봇 시스템

이 모듈은 LangChain, OpenAI API, ChromaDB를 사용하여
학생들의 학사 관련 질문에 답변하는 RAG 시스템을 제공합니다.
"""

import json
import os
from typing import Dict, List, Any
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document

# 환경 변수 로드
load_dotenv()


class RAGSystem:
    """RAG 기반 질의응답 시스템"""

    def __init__(self, data_path: str = "data/sample_data.json",
                 vectorstore_path: str = "vectorstore"):
        """
        RAG 시스템 초기화

        Args:
            data_path: JSON 데이터 파일 경로
            vectorstore_path: 벡터 DB 저장 경로
        """
        print("🚀 RAG 시스템을 초기화하는 중...")

        self.data_path = data_path
        self.vectorstore_path = vectorstore_path

        # OpenAI API 키 확인
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("❌ OPENAI_API_KEY가 .env 파일에 설정되지 않았습니다!")

        # OpenAI Embeddings 설정
        print("📝 임베딩 모델 설정 중 (text-embedding-3-small)...")
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small"
        )

        # OpenAI LLM 설정
        print("🤖 LLM 모델 설정 중 (gpt-4o-mini)...")
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3
        )

        # 벡터 DB 로드 또는 생성
        self.vectorstore = self._load_or_create_vectorstore()

        # QA 체인 생성
        print("⚙️ QA 체인 생성 중...")
        self.qa_chain = self._create_qa_chain()

        print("✅ RAG 시스템 초기화 완료!\n")

    def _load_or_create_vectorstore(self) -> Chroma:
        """
        벡터 DB 로드 또는 생성

        Returns:
            Chroma 벡터스토어 인스턴스
        """
        if os.path.exists(self.vectorstore_path):
            print("📂 기존 벡터 DB를 로드하는 중...")
            return Chroma(
                persist_directory=self.vectorstore_path,
                embedding_function=self.embeddings
            )
        else:
            print("🔨 새로운 벡터 DB를 생성하는 중...")
            return self._create_vectorstore()

    def _create_vectorstore(self) -> Chroma:
        """
        JSON 데이터로부터 벡터 DB 생성

        Returns:
            Chroma 벡터스토어 인스턴스
        """
        # JSON 데이터 로드
        print(f"📖 데이터 파일 로드 중: {self.data_path}")
        with open(self.data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        print(f"📊 총 {len(data)}개의 문서를 발견했습니다.")

        # Document 객체 생성
        documents = []
        for item in data:
            doc = Document(
                page_content=item['content'],
                metadata={
                    'source': item['url'],
                    'title': item['title']
                }
            )
            documents.append(doc)

        # 텍스트 분할
        print("✂️ 텍스트를 청크로 분할하는 중...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            length_function=len
        )
        splits = text_splitter.split_documents(documents)
        print(f"📝 총 {len(splits)}개의 청크가 생성되었습니다.")

        # ChromaDB에 배치로 저장 (OpenAI API 토큰 제한 회피)
        print("💾 벡터 DB에 저장하는 중 (배치 처리)...")

        # 첫 번째 배치로 vectorstore 생성
        batch_size = 100  # 한 번에 처리할 청크 수

        if len(splits) > 0:
            # 첫 배치로 vectorstore 초기화
            first_batch = splits[:batch_size]
            vectorstore = Chroma.from_documents(
                documents=first_batch,
                embedding=self.embeddings,
                persist_directory=self.vectorstore_path
            )
            print(f"  ✓ 배치 1/{(len(splits)-1)//batch_size + 1} 완료 ({len(first_batch)}개 청크)")

            # 나머지 배치 추가
            for i in range(batch_size, len(splits), batch_size):
                batch = splits[i:i+batch_size]
                vectorstore.add_documents(batch)
                batch_num = i//batch_size + 1
                total_batches = (len(splits)-1)//batch_size + 1
                print(f"  ✓ 배치 {batch_num}/{total_batches} 완료 ({len(batch)}개 청크)")

        print(f"✅ 벡터 DB 생성 완료! (저장 경로: {self.vectorstore_path})")
        print(f"📦 총 {len(splits)}개의 청크가 저장되었습니다.")
        return vectorstore

    def _create_qa_chain(self) -> RetrievalQA:
        """
        QA 체인 생성

        Returns:
            RetrievalQA 체인 인스턴스
        """
        # 한국어 프롬프트 템플릿
        template = """당신은 동양대학교의 친절한 AI 도우미입니다.
학생들의 학사 관련 질문에 정확하고 친절하게 답변해주세요.

다음 규칙을 반드시 따라주세요:
1. 주어진 정보만을 바탕으로 답변하세요.
2. 정보가 없으면 "제공된 정보에서는 해당 내용을 찾을 수 없습니다"라고 정직하게 답변하세요.
3. 답변은 한국어로 자연스럽고 친절하게 작성하세요.
4. 가능한 경우 구체적인 날짜, 시간, 연락처 등을 포함하세요.

참고 정보:
{context}

질문: {question}

답변:"""

        PROMPT = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )

        # RetrievalQA 체인 구성
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(
                search_kwargs={"k": 3}  # Top-3 문서 검색
            ),
            return_source_documents=True,
            chain_type_kwargs={"prompt": PROMPT}
        )

        return qa_chain

    def ask(self, question: str) -> Dict[str, Any]:
        """
        질문에 대한 답변 생성

        Args:
            question: 사용자 질문

        Returns:
            답변과 출처를 포함한 딕셔너리
        """
        print(f"\n❓ 질문: {question}")
        print("🔍 답변을 생성하는 중...")

        # QA 체인 실행
        result = self.qa_chain.invoke({"query": question})

        # 답변 추출
        answer = result['result']

        # 출처 문서 추출
        sources = []
        for doc in result['source_documents']:
            sources.append({
                'title': doc.metadata.get('title', 'Unknown'),
                'source': doc.metadata.get('source', 'Unknown'),
                'content': doc.page_content[:200] + '...' if len(doc.page_content) > 200 else doc.page_content
            })

        print(f"✅ 답변 생성 완료!\n")

        return {
            'answer': answer,
            'sources': sources
        }

    def reset_vectorstore(self) -> None:
        """벡터 DB 재생성"""
        print("🔄 벡터 DB를 재생성하는 중...")

        # 기존 벡터 DB 삭제
        if os.path.exists(self.vectorstore_path):
            import shutil
            shutil.rmtree(self.vectorstore_path)
            print("🗑️ 기존 벡터 DB 삭제 완료")

        # 새로운 벡터 DB 생성
        self.vectorstore = self._create_vectorstore()

        # QA 체인 재생성
        self.qa_chain = self._create_qa_chain()

        print("✅ 벡터 DB 재생성 완료!\n")


def main():
    """대화형 인터페이스 (터미널)"""
    print("=" * 60)
    print("🎓 동양대학교 AI 도우미")
    print("=" * 60)
    print()

    # RAG 시스템 초기화
    try:
        rag = RAGSystem()
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return

    print("💬 질문을 입력하세요 (종료하려면 'quit' 입력)")
    print("-" * 60)

    # 대화 루프
    while True:
        try:
            # 사용자 입력
            question = input("\n질문: ").strip()

            # 종료 조건
            if question.lower() in ['quit', 'exit', '종료', 'q']:
                print("\n👋 동양대학교 AI 도우미를 종료합니다.")
                break

            # 빈 입력 처리
            if not question:
                print("⚠️ 질문을 입력해주세요.")
                continue

            # 답변 생성
            result = rag.ask(question)

            # 답변 출력
            print("\n" + "=" * 60)
            print("💡 답변:")
            print(result['answer'])

            # 출처 출력
            if result['sources']:
                print("\n📚 참고 문서:")
                for i, source in enumerate(result['sources'], 1):
                    print(f"\n{i}. {source['title']}")
                    print(f"   🔗 {source['source']}")

            print("=" * 60)

        except KeyboardInterrupt:
            print("\n\n👋 동양대학교 AI 도우미를 종료합니다.")
            break
        except Exception as e:
            print(f"\n❌ 오류 발생: {e}")


if __name__ == "__main__":
    main()