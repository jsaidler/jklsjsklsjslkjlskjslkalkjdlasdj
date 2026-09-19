# Next chat handoff — Video Studio local behavioral route

Date: **2026-09-18**  
Status: **READY TO CONTINUE / PREFLIGHT PASSED / BEHAVIOR PROFILE NEXT**

Paste the prompt below into the next chat.

---

## Continuation prompt

Continue o projeto **Local Video Studio** exatamente do estado canônico no GitHub `jsaidler/jklsjsklsjslkjlskjslkalkjdlasdj`, branch `main`.

Antes de responder ou propor qualquer alteração, leia integralmente, nesta ordem:

1. `docs/PROJECT_STATE.md`
2. `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`
3. `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_ROUTE_2026-09-18.md`
4. `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_PREFLIGHT_2026-09-18.md`
5. `docs/VIDEO_STUDIO_DIRECTION_RESET_2026-09-15.md`
6. `docs/VIDEO_STUDIO.md`
7. `docs/VIDEO_STUDIO_QUALITY_GATE_2026-09-15.md`
8. `tools/video-studio/preflight_local_behavior_route.ps1`

Não reconstrua decisões por memória se os documentos disserem algo diferente. Atualize os documentos vivos sempre que o estado mudar.

### Restrições inegociáveis

O projeto é **100% local/self-hosted e sem custos de serviço**. Não usar HeyGen, Kling, APIs pagas, créditos, assinaturas, SaaS/cloud inference ou qualquer plataforma externa de geração/treino/avatar. Não enviar vídeos, voz ou identidade do João para terceiros. Internet pode ser usada apenas para pesquisa/documentação e download de componentes gratuitos que rodem localmente. Não escolher software/modelo/licença paga sem autorização explícita prévia.

### Objetivo real

Gerar vídeos novos a partir de novo texto/áudio em que o resultado:

- pareça visualmente com João;
- soe como João;
- **mova-se e expresse-se como João**, preservando sua identidade comportamental real.

Movimento apenas plausível ou “natural” não basta. O benchmark Wan2.2-S2V 20-step já mostrou isso: visualmente ficou muito próximo, mas as expressões e movimentos eram de outra pessoa porque o teste recebeu imagem estática + áudio, sem vídeo comportamental.

### Arquitetura escolhida

A primeira implementação é um **behavior compiler / behavioral driver synthesis**:

```text
vídeos reais do João
    -> pose + prosódia
    -> biblioteca de motion units do próprio João

novo áudio local
    -> janelas prosódicas
    -> busca/ordenação de motion units compatíveis
    -> continuidade de pose + diversidade
    -> novo driving video composto da linguagem corporal real do João

novo driving video
    -> Wan-Animate-2 já instalado
    -> lip-sync local depois, se necessário
```

Não usar um único driving clip fixo. O objetivo é montar uma performance nova a partir do vocabulário comportamental real registrado nos vídeos do João.

### Fontes comportamentais canônicas

Pasta:

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\`

Originais protegidos:

- `VID_20260911_140124885.mp4` — 300.4 s, 3840x2160 HEVC + áudio — **fonte principal de tronco/mãos/postura/gestos**;
- `VID_20260819_124008056.mp4` — 282.6 s, 1920x1080 H.264 + áudio — **fonte facial/microexpressões**;
- `SIENA_BRUTO.mp4` — 113.3 s, 1080x1920 H.264 + áudio — **gestos/visual alternativo**, com spans de objetos/oclusões a excluir quando necessário.

Existe também uma derivada local H.264 1080p de 1.48 GB sob o caminho histórico `avatar_v`; o nome HeyGen é apenas histórico e não autoriza qualquer uso externo.

### Preflight concluído em 2026-09-18 23:45

Resultado canônico:

```text
BEHAVIOR SOURCES: PASS
WAN-ANIMATE-2 PAYLOAD: PASS
WAN-ANIMATE-2 NATIVE CODE: PASS
POSE TOOLING: NOT FOUND UNDER WAN ROOT
NEXT ROUTE GATE: BUILD BEHAVIOR PROFILE WITHOUT NEW LARGE RENDERER DOWNLOAD
```

Hardware/runtime observado:

- Windows 11;
- RTX 3060 12 GB;
- driver NVIDIA 595.95;
- VRAM no preflight: 12288 MB total / 11579 MB livre;
- Z: apenas 22.32 GB livres;
- ffmpeg/ffprobe/nvidia-smi presentes.

Wan-Animate-2 reutilizável:

- `Z:\AI\WanAnimate2\models\diffusion_models\wan_animate_2_bf16.safetensors` — 30.538 GiB;
- `Z:\AI\WanAnimate2\models\text_encoders\umt5_xxl_fp16.safetensors` — 10.586 GiB;
- `Z:\AI\WanAnimate2\models\vae\Wan2_1_VAE_bf16.safetensors` — 0.236 GiB;
- `Z:\AI\WanAnimate2\comfy\ldm\wan\model_animate2.py` — presente.

Não baixar outro renderer grande. VACE/Motion Mirror permanece fallback apenas.

### Atenção: Python

O preflight imprimiu:

`Python 3.11: PASS / C:\Python314\python.exe / 3.14.3`

Isso é inconsistente. Antes de instalar/usar tooling Python novo para pose/prosódia, resolva explicitamente qual interpretador/venv deve ser usado. Não considere Python 3.11 validado apenas pelo rótulo do relatório.

### Pose tooling

DWPose/whole-body model **não foi encontrado sob `Z:\AI\WanAnimate2`**. Isso não prova ausência global porque o preflight evitou varrer todo `Z:\AI`.

Primeiro faça uma busca direcionada/no-download nos roots locais prováveis. Se realmente não houver pose tooling reutilizável e DWPose for necessário, ele é um componente pequeno (~350 MB), não um renderer. Antes de baixar qualquer coisa, enumere arquivo exato, fonte oficial, licença, tamanho, destino e espaço final. Não baixe automaticamente.

### Disco

Z: tem ~22.32 GB livres. Existe payload Hunyuan aposentado e potencialmente recuperável:

`Z:\AI\WanGP\ckpts\hunyuan_video_avatar_720_quanto_bf16_int8.safetensors` — 12.486 GiB.

Não apagar por reflexo, mas ele é o primeiro candidato de limpeza se houver necessidade real de espaço, pois Hunyuan local já foi classificado como `FUNCTIONAL RUNTIME PASS / NO VISUAL VERDICT / LOCAL PRACTICALITY FAIL`.

### O que fazer agora

A próxima etapa NÃO é outro benchmark de renderização e NÃO é escolher outro modelo grande. É construir o primeiro **behavior profile / motion-unit extractor** dentro de `tools/video-studio/`.

Faça o trabalho em etapas verificáveis:

1. leia o código atual e o preflight;
2. resolva a inconsistência do Python sem instalar coisas cegamente;
3. procure pose tooling reutilizável localmente antes de qualquer download;
4. defina um schema persistente para o perfil e as motion units;
5. implemente o extractor primeiro para `VID_20260911_140124885.mp4`;
6. cada motion unit deve guardar pelo menos: source file, timestamps, RGB clip reference, pose inicial/final, movimento de cabeça, atividade de mãos/corpo, energia de movimento e descritores de fala/prosódia;
7. corte unidades em pausas/baixa energia e pontos de transição que favoreçam continuidade;
8. produza um inventário inspectável/manifest antes de qualquer render Wan;
9. só depois construa a seleção/concatenação de unidades para formar um driving video novo de ~4–5 s;
10. então faça um primeiro gate curto no Wan-Animate-2 já instalado.

MuseTalk/LatentSync e CosyVoice continuam **deferidos**. Primeiro provar corpo/cabeça/comportamento. Lip-sync e voz entram depois.

### Regra de qualidade

Não aceite um resultado por ser anatomicamente plausível. O gate humano continua:

> “isso não apenas parece João; isso se move e reage como João.”

### Forma de trabalho

- Use o GitHub para ler e atualizar os documentos canônicos.
- Não crie decisões paralelas em chat: edite os documentos vivos.
- Se alterar o repositório remotamente, nos comandos para Windows sempre comece com:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'

git pull --ff-only origin main
```

- Prefira scripts `.ps1`/`.py` versionados no repositório, não blocos enormes inline de PowerShell.
- Se um script falhar, corrija o repositório em vez de pedir depuração manual extensa.
- Antes de qualquer download/instalação, diga exatamente o que será baixado, tamanho aproximado, destino, licença e por que é necessário.
- Não execute/decrete limpeza de arquivos pessoais ou originais comportamentais.

Comece pela leitura dos documentos e **continue diretamente da etapa “behavior profile / motion-unit extractor”**. Não volte a HeyGen, Wan S2V, H3 ou Hunyuan e não reabra decisões já fechadas sem nova evidência técnica.