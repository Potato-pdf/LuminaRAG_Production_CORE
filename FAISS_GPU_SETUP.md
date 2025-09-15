🚀 GUÍA DE INSTALACIÓN FAISS-GPU
================================

## ⚡ REQUISITOS PREVIOS

### 1. **Hardware Necesario**
- GPU NVIDIA con soporte CUDA
- Mínimo 4GB de VRAM (recomendado 8GB+)
- Driver NVIDIA actualizado

### 2. **Software Base**
- CUDA Toolkit 11.8+ o 12.x
- cuDNN compatible
- Python 3.8+

## 🔧 INSTALACIÓN PASO A PASO

### Opción 1: Conda (Recomendado)
```bash
# Crear entorno con dependencias GPU
conda create -n lumina_gpu python=3.9
conda activate lumina_gpu

# Instalar PyTorch con soporte CUDA
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia

# Instalar FAISS-GPU
conda install -c conda-forge faiss-gpu

# Instalar dependencias del proyecto
pip install -r requirements.txt
```

### Opción 2: Pip (Alternativa)
```bash
# Verificar CUDA disponible
nvidia-smi

# Instalar PyTorch GPU
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Instalar FAISS-GPU
pip install faiss-gpu==1.8.0

# Instalar dependencias restantes
pip install -r requirements.txt
```

## ✅ VERIFICACIÓN DE INSTALACIÓN

### Test Rápido FAISS-GPU:
```python
import faiss
import torch

# Verificar CUDA
print(f"CUDA disponible: {torch.cuda.is_available()}")
print(f"GPUs detectadas: {torch.cuda.device_count()}")

# Verificar FAISS-GPU
print(f"FAISS GPUs: {faiss.get_num_gpus()}")
```

### Test en el Sistema:
```bash
# Verificar sistema completo
python3 -c "
from src.FAISS.tree_graph import TreeGraphRAG
import faiss
print(f'FAISS GPUs disponibles: {faiss.get_num_gpus()}')
"
```

## 🎯 CONFIGURACIÓN OPTIMIZADA

### Variables de Entorno (Opcional):
```bash
# Para optimizar rendimiento GPU
export CUDA_VISIBLE_DEVICES=0  # Usar GPU específica
export FAISS_OMP_NUM_THREADS=8  # Threads para operaciones CPU
```

### Ajustes de Memoria:
```python
# En caso de problemas de memoria GPU
import torch
torch.cuda.empty_cache()  # Limpiar cache GPU
```

## 🚨 SOLUCIÓN DE PROBLEMAS

### Error: "No CUDA-capable device"
```bash
# Verificar instalación NVIDIA
nvidia-smi
nvcc --version

# Reinstalar drivers si es necesario
sudo apt update && sudo apt install nvidia-driver-xxx
```

### Error: "FAISS not compiled with GPU support"
```bash
# Desinstalar versión CPU e instalar GPU
pip uninstall faiss-cpu faiss-gpu
conda install -c conda-forge faiss-gpu
```

### Error: "CUDA out of memory"
```bash
# Reducir batch size o usar GPU con más VRAM
# El sistema automáticamente fallback a CPU si es necesario
```

## 📊 BENCHMARK ESPERADO

### Rendimiento GPU vs CPU:
- **Indexación**: 5-10x más rápida
- **Búsqueda**: 10-50x más rápida  
- **Memoria**: Más eficiente para datasets grandes

### Casos de Uso Óptimos:
- ✅ 100+ documentos
- ✅ Consultas frecuentes
- ✅ Embeddings de alta dimensión (768+)
- ✅ Múltiples usuarios concurrentes

## 🎮 CONFIGURACIÓN GAMING/CONSUMER GPU

### Para RTX 3060/4060 (8GB VRAM):
```python
# Configuración conservadora
batch_size = 32
max_documents = 500
embedding_dim = 768
```

### Para RTX 3070/4070+ (12GB+ VRAM):
```python
# Configuración agresiva
batch_size = 64
max_documents = 2000
embedding_dim = 1024
```

## 💡 TIPS DE OPTIMIZACIÓN

1. **Usar FP16**: Reduce uso de memoria a la mitad
2. **Batch Processing**: Procesar múltiples queries juntas
3. **Index Caching**: Mantener índice en GPU entre consultas
4. **Memory Pooling**: Reutilizar buffers GPU

## 🔄 FALLBACK AUTOMÁTICO

El sistema incluye fallback automático:
- Si GPU no disponible → CPU
- Si memoria insuficiente → CPU
- Si error CUDA → CPU con warning

## 📱 MONITOREO GPU

```bash
# Monitor en tiempo real
watch -n 1 nvidia-smi

# Log de uso
nvidia-smi --query-gpu=timestamp,utilization.gpu,memory.used --format=csv -l 1
```

## 🎯 RESULTADO ESPERADO

✅ **Configuración exitosa**:
```
🚀 SISTEMA FAISS-GPU + ÁRBOLES JERÁRQUICOS
==================================================
📄 Total documentos: X
🌿 Raíces indexadas: X  
🚀 Aceleración GPU: ✅ (1 GPUs)
⚡ Tipo índice: GPU
⚡ Estado: ✅ Listo
```

## 🆘 SOPORTE

Si tienes problemas:
1. Verificar `nvidia-smi`
2. Ejecutar tests de verificación
3. Revisar logs de CUDA
4. El sistema fallback a CPU funcionará siempre