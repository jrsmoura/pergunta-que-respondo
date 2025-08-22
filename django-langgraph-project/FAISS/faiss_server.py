from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import faiss

# Inicia a aplicação FastAPI
app = FastAPI()

# Cria o índice FAISS na memória (exemplo com 128 dimensões)
d = 128
index = faiss.IndexFlatL2(d)

class VectorData(BaseModel):
    vector: list[float]
    metadata: dict

@app.post("/add_vector")
def add_vector(data: VectorData):
    if len(data.vector) != d:
        raise HTTPException(status_code=400, detail=f"O vetor deve ter {d} dimensões.")

    vector_array = np.array([data.vector], dtype='float32')
    index.add(vector_array)

    return {"status": "success", "message": f"Vetor adicionado. Total de vetores: {index.ntotal}"}

@app.get("/search")
def search_vector(vector: str, k: int = 1):
    try:
        query_vector = np.array([float(v) for v in vector.split(',')], dtype='float32').reshape(1, -1)
        D, I = index.search(query_vector, k)
        return {"distances": D.tolist(), "indices": I.tolist()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))