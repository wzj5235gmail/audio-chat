exp_name = "Suou_Yuki"
video_path = r"C:\Users\Administrator\Downloads\yuki-2.mp4"

exp_root = "logs"
device = "cuda:0"
separate_audio_is_half = True
uvr5_model = "HP5_only_main_vocal"
uvr5_agg = 10
output_format = "wav"
conda_env = "pyannote"

asr_model_size = "large"
asr_language = "auto"
asr_precision = "float32"

bert_pretrained_dir = "GPT_SoVITS/pretrained_models/chinese-roberta-wwm-ext-large"
ssl_pretrained_dir = "GPT_SoVITS/pretrained_models/chinese-hubert-base"
pretrained_s2G_path = "GPT_SoVITS/pretrained_models/s2G488k.pth"
num_processes = 1
process_index = 0
separate_audio_is_half = True

sovits_batch_size = 8
sovits_total_epoch = 15
sovits_text_low_lr_rate = 0.4
sovits_if_save_latest = True
sovits_if_save_every_weights = True
sovits_save_every_epoch = 4
sovits_gpu_numbers = "0-1"
pretrained_s2G_path = "GPT_SoVITS/pretrained_models/s2G488k.pth"
pretrained_s2D_path = "GPT_SoVITS/pretrained_models/s2D488k.pth"
python_exec = "runtime/python.exe"
train_sovits_is_half = True
sovits_temp_dir = "TEMP"
sovits_weight_root = "SoVITS_weights"

gpt_batch_size = 8
gpt_total_epoch = 15
gpt_if_dpo = False
gpt_if_save_latest = True
gpt_if_save_every_weights = True
gpt_save_every_epoch = 5
gpt_gpu_numbers = "0"
pretrained_s1_path = "GPT_SoVITS/pretrained_models/s1bert25hz-2kh-longer-epoch=68e-step=50232.ckpt"
python_exec = "runtime/python.exe"
train_gpt_is_half = True
gpt_temp_dir = "TEMP"
gpt_weight_root = "GPT_weights"
