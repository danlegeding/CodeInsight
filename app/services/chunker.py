from langchain_text_splitters import RecursiveCharacterTextSplitter
"""
切分器：先将一个代码文件的所有内容按照指定长度切分，然后通过检查里面的\n查看行数
最后返回CodeChunk对象列表   
注意点：1.注意split_text和create_documents的区别(还有split_documents)
2. 关注document内容的格式
"""
def chunk_code(
        content:str,
        chunk_size:int=500,
        overlap:int=50
)->list[dict]:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        add_start_index=True,
    )

    documents = text_splitter.create_documents([content])
    result = []
    for i, document in enumerate(documents):
        chunk=document.page_content
        start_index=document.metadata["start_index"]

        start_line = content[:start_index].count("\n")+1
        end_index = start_index + len(chunk)
        end_line = content[:end_index].count("\n")+1
        mid_result = {
            "content":chunk,
            "start_line":start_line,
            "end_line":end_line,
            "chunk_index":i
        }
        result.append(mid_result)
    return result