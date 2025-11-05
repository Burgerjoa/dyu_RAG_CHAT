from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import json
import os


class RAGSystem:
    def __init__(self, data_path="data/sample_data.json", vectorstore_path="./vectorstore"):
        """RAG 시스템 초기화"""
        self.data_path = data_path
        self.vectorstore_path = vectorstore_path
        self.embeddings = None
        self.llm = None
        self.vectorstore = None
        self.qa_chain = None

        print("🚀 RAG 시스템 초기화 시작...")
        self._setup()

    def _setup(self):
        """전체 시스템 설정"""
        # 1. 임베딩 모델 로드
        print("📊 임베딩 모델 로딩 중... (처음엔 다운로드로 시간 걸림)")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="jhgan/ko-sroberta-multitask",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        print("✅ 임베딩 모델 로드 완료!")

        # 2. Ollama LLM 설정
        print("🦙 Ollama 연결 중...")
        self.llm = Ollama(
            model="llama3.2:3b",
            temperature=0.7,
        )
        print("✅ Ollama 연결 완료!")

        # 3. 벡터 DB 로드 또는 생성
        if os.path.exists(self.vectorstore_path):
            print("📂 기존 벡터 DB 로드 중...")
            self.vectorstore = Chroma(
                persist_directory=self.vectorstore_path,
                embedding_function=self.embeddings
            )
            print("✅ 벡터 DB 로드 완료!")
        else:
            print("🔨 새 벡터 DB 생성 중...")
            self._create_vectorstore()

        # 4. QA 체인 생성
        self._create_qa_chain()
        print("🎉 RAG 시스템 준비 완료!\n")

    def _create_vectorstore(self):
        """데이터에서 벡터 DB 생성"""
        # 데이터 로드
        print(f"📖 데이터 로드 중: {self.data_path}")
        with open(self.data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ {len(data)}개 문서 로드 완료")

        # 텍스트 분할
        print("✂️  텍스트 분할 중...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            length_function=len,
        )

        texts = []
        metadatas = []

        for item in data:
            # 제목과 내용 합치기
            full_text = f"제목: {item['title']}\n\n{item['content']}"

            # 청크로 분할
            chunks = text_splitter.split_text(full_text)

            for chunk in chunks:
                texts.append(chunk)
                metadatas.append({
                    'source': item['url'],
                    'title': item['title']
                })

        print(f"✅ 총 {len(texts)}개 청크 생성")

        # 벡터 DB 생성
        print("🔮 벡터 DB 생성 중... (시간 좀 걸림)")
        self.vectorstore = Chroma.from_texts(
            texts=texts,
            embedding=self.embeddings,
            metadatas=metadatas,
            persist_directory=self.vectorstore_path
        )
        self.vectorstore.persist()
        print("✅ 벡터 DB 생성 완료!")

    def _create_qa_chain(self):
        """QA 체인 생성"""
        # 한국어 프롬프트 템플릿
        template = """당신은 동양대학교 학생들을 돕는 친절한 AI 도우미입니다.
주어진 정보를 바탕으로 질문에 답변해주세요.

정보:
{context}

질문: {question}

답변 규칙:
1. 반드시 한국어로 답변하세요
2. 주어진 정보를 바탕으로만 답변하세요
3. 정보에 없는 내용은 "해당 정보를 찾을 수 없습니다"라고 답하세요
4. 친절하고 자연스럽게 답변하세요
5. 답변 끝에 출처를 언급하세요

답변:"""

        prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )

        # QA 체인 생성
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(
                search_kwargs={"k": 3}  # 상위 3개 문서 검색
            ),
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt}
        )

    def ask(self, question):
        """질문하기"""
        print(f"\n❓ 질문: {question}")
        print("🔍 검색 중...")

        result = self.qa_chain({"query": question})

        answer = result['result']
        sources = result['source_documents']

        print(f"💬 답변: {answer}\n")

        # 출처 표시
        if sources:
            print("📚 출처:")
            seen_sources = set()
            for doc in sources:
                source = doc.metadata.get('source', 'Unknown')
                title = doc.metadata.get('title', 'Unknown')
                if source not in seen_sources:
                    print(f"  - {title}: {source}")
                    seen_sources.add(source)

        return {
            'answer': answer,
            'sources': [
                {
                    'title': doc.metadata.get('title', 'Unknown'),
                    'url': doc.metadata.get('source', 'Unknown')
                }
                for doc in sources
            ]
        }

    def reset_vectorstore(self):
        """벡터 DB 초기화 (새 데이터 투입 시 사용)"""
        import shutil
        if os.path.exists(self.vectorstore_path):
            shutil.rmtree(self.vectorstore_path)
            print("🗑️  기존 벡터 DB 삭제 완료")
        self._create_vectorstore()
        self._create_qa_chain()
        print("✅ 새 벡터 DB 생성 완료")


# 테스트용 메인 함수
if __name__ == "__main__":
    # RAG 시스템 초기화
    rag = RAGSystem()

    # 대화형 테스트
    print("=" * 60)
    print("동양대학교 AI 도우미 (종료: 'quit' 입력)")
    print("=" * 60)

    while True:
        question = input("\n질문을 입력하세요: ")

        if question.lower() in ['quit', 'exit', '종료', 'q']:
            print("👋 안녕히 가세요!")
            break

        if not question.strip():
            continue

        rag.ask(question)