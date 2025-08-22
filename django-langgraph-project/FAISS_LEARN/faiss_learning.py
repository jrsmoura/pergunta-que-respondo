# Criação dos valores para o banco
import numpy as np
d = 64                           # dimensão dos vetores
nb = 100000                      # tamanho da base de dados
nq = 10000                       # número de consultas
np.random.seed(1234)             # tornar reproduzível
xb = np.random.random((nb, d)).astype('float32') # criando vetores aleatórios
xb[:, 0] += np.arange(nb) / 1000. # adicionando ruído
xq = np.random.random((nq, d)).astype('float32') # criando vetores aleatórios
xq[:, 0] += np.arange(nq) / 1000. # adicionando ruído


## exemplo simples de busca
import faiss                   # Importando faiss
index = faiss.IndexFlatL2(d)   # construindo o index
print(index.is_trained)        # verificação de treinamento
index.add(xb)                  # adicionando vetores ao index
print(index.ntotal)


k = 4                          # queremos ver 4 vizinhos mais próximos
D, I = index.search(xb[:5], k) # verificação de sanidade
print(I)
print(D)
D, I = index.search(xq, k)     # busca real
print(I[:5])                   # vizinhos das 5 primeiras consultas
print(I[-5:])                  # vizinhos das 5 últimas consultas

## Exemplo mais rápido
nlist = 100
quantizer = faiss.IndexFlatL2(d)  # outros índices
index = faiss.IndexIVFFlat(quantizer, d, nlist) # Implementação da adição de vetores onde as atribuições dos vetores são predefinidas
assert not index.is_trained # Ainda não foir treinado
index.train(xb) # treinando o indice
assert index.is_trained  # treinamento feito

index.add(xb)                  # adicionar talvez deixe mais lento
D, I = index.search(xq, k)     # busca real
print(I[-5:])                  # vizinhos das 5 últimas consultas
index.nprobe = 10              # nprobe padrão é 1, tente alguns a mais
D, I = index.search(xq, k)
print(I[-5:])                  # neighbors of the 5 last queries

## Lower memory footprint
m = 8                             # número de subquantizers
quantizer = faiss.IndexFlatL2(d)  # continua o mesmo
index = faiss.IndexIVFPQ(quantizer, d, nlist, m, 8)
                                    # 8 especifica que cada sub-vetor é codificado como 8 bits
index.train(xb)
index.add(xb)
D, I = index.search(xb[:5], k) # verificação de sanidade
print(I)
print(D)
index.nprobe = 10              # torna comparável com o experimento acima
D, I = index.search(xq, k)     # busca
print(I[-5:])