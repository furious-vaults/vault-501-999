import os
import subprocess
import time

# --- CONFIGURAÇÃO ---
LOTE_TAMANHO = 100  # Quantos jogos subir por vez
BRANCH = "main"    # Normalmente 'main' ou 'master'

def run_git_push(force=False):
    """Executa o push permitindo que o usuário veja o progresso real na tela."""
    cmd = f"git push {'-f' if force else ''} origin {BRANCH}"
    print(f">> Executando: {cmd}")
    try:
        # Usamos shell=True para compatibilidade com Windows
        result = subprocess.run(cmd, shell=True)
        return result.returncode == 0
    except Exception as e:
        print(f"Erro ao executar push: {e}")
        return False

def push_fatiado():
    print(f"--- INICIANDO PUSH FATIADO V4 (RESUME AUTO-SKIP) ---")
    
    if not os.path.exists("vault"):
        print("ERRO: Pasta 'vault' não encontrada. Verifique se está na raiz do repositório.")
        return

    # 1. Garante que o branch se chama 'main'
    print("[*] Garantindo branch local 'main'...")
    subprocess.run("git branch -m main", shell=True, capture_output=True)

    prefixos = [d for d in os.listdir("vault") if os.path.isdir(os.path.join("vault", d))]
    prefixos.sort()

    for p in prefixos:
        caminho_prefixo = os.path.join("vault", p)
        jogos = [j for j in os.listdir(caminho_prefixo) if os.path.isdir(os.path.join(caminho_prefixo, j))]
        jogos.sort()
        
        for i in range(0, len(jogos), LOTE_TAMANHO):
            lote = jogos[i : i + LOTE_TAMANHO]
            print(f"\n[*] Analisando lote {i//LOTE_TAMANHO + 1} do prefixo '{p}' ({len(lote)} jogos)...")
            
            # 1. Adiciona os jogos ao índice
            for jogo in lote:
                subprocess.run(f'git add "vault/{p}/{jogo}"', shell=True, capture_output=True)
            
            # 2. Tenta fazer o commit
            msg = f"Upload Lote {i//LOTE_TAMANHO + 1} - Prefixo {p}"
            # Capturamos a saída para saber se houve mudanças
            result_commit = subprocess.run(f'git commit -m "{msg}"', shell=True, capture_output=True, text=True)
            
            # Se não houver nada novo, pulamos o push para ganhar tempo
            if "nothing to commit" in result_commit.stdout or "nada para fundamentar" in result_commit.stdout or "working tree clean" in result_commit.stdout:
                print(f"[-] Lote {i//LOTE_TAMANHO + 1} do prefixo {p} já enviado. Pulando...")
                continue

            # 3. Se houver commit novo, faz o push
            print(f"[+] Novos arquivos detectados. Iniciando upload...")
            tentativas = 3
            while tentativas > 0:
                if run_git_push(force=True):
                    print(f"[OK] Lote {i//LOTE_TAMANHO + 1} do prefixo {p} finalizado.")
                    break
                else:
                    print(f"!! Falha na conexão (Tentativa {4-tentativas}/3). Aguardando...")
                    time.sleep(10)
                    tentativas -= 1
            
            if tentativas == 0:
                print("\n[!] O GitHub recusou muitos envios. Verifique sua conexão e rode novamente para CONTINUAR de onde parou.")
                return

    print("\n--- PROCESSO CONCLUÍDO! Seu Vault deve estar 100% no GitHub agora. ---")

if __name__ == "__main__":
    push_fatiado()
