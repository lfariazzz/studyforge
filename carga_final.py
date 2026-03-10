from src.database.RepositorioGeral import RepositorioGeral
from src.models.municipio import Municipio
from src.models.escola import Escola
from src.models.escola_endereco import Endereco
from src.models.gestor import Gestor

repo = RepositorioGeral()

# 1. MUNICÍPIO
mun = Municipio("Juazeiro do Norte", "CE", 1000000.0, 7.5)
repo.salvar_municipio(mun)

# 2. ESCOLA (Salvando ANTES do gestor)
end = Endereco(None, None, "63000-000", "Rua Central", "100", "Centro")
esc = Escola("Escola Farias Brito", end, None, None, 50000.0, mun._id_municipio, 800, mun)
repo.salvar_escola(esc) 
# AGORA esc._id_escola EXISTE!

# 3. GESTOR (Beatriz)
beatriz = Gestor(None, "Beatriz Souza", "200.000.000-01", "gestor1@edu.com", "senha123", "8899999999", "10/10/1980", esc)
repo.salvar_usuario(beatriz) 
# O repo do seu amigo vai ler esc._id_escola e salvar o número 1 no banco.