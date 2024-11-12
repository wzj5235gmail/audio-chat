from faster_whisper import WhisperModel
from feature_extractor import cnhubert
from glob import glob
import json
import librosa
import logging
import numpy as np
import os
from subprocess import Popen
import shutil
from scipy.io import wavfile
import torch
from time import time as ttime
import traceback
from transformers import AutoModelForMaskedLM, AutoTokenizer
from tqdm import tqdm
from text.cleaner import clean_text
from tools.asr.config import check_fw_local_models
from tools.my_utils import load_audio
import utils
import yaml
from module.models import SynthesizerTrn
import RUNALL_CONFIG as config

# 设置日志
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

exp_root = config.exp_root
exp_name = config.exp_name

############################## 语音识别 ###############################


os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"


def execute_asr(
    input_folder=f"output/slicer_opt/{exp_name}",
    output_folder=f"output/asr_opt/{exp_name}",
    model_size=config.asr_model_size,
    language=config.asr_language,
    precision=config.asr_precision,
):
    logger.info("开始语音识别处理...")
    if "-local" in model_size:
        model_size = model_size[:-6]
        model_path = f"tools/asr/models/faster-whisper-{model_size}"
    else:
        model_path = model_size
    if language == "auto":
        language = None  # 不设置语种由模型自动输出概率最高的语种
    logger.info(f"加载 Faster Whisper 模型: {model_size} {model_path}")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    try:
        model = WhisperModel(model_path, device=device, compute_type=precision)
    except:
        logger.error(traceback.format_exc())
        return print(traceback.format_exc())

    input_file_names = os.listdir(input_folder)
    input_file_names.sort()
    logger.info(f"找到 {len(input_file_names)} 个输入文件")

    output = []
    output_file_name = os.path.basename(input_folder)

    for file_name in tqdm(input_file_names):
        try:
            file_path = os.path.join(input_folder, file_name)
            logger.debug(f"处理文件: {file_path}")
            segments, info = model.transcribe(
                audio=file_path,
                beam_size=5,
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=700),
                language=language,
            )
            text = ""

            if info.language == "zh":
                logger.info("检测为中文文本, 转 FunASR 处理")
                if "only_asr" not in globals():
                    from tools.asr.funasr_asr import (
                        only_asr,
                    )  # #如果用英文就不需要导入下载模型
                text = only_asr(file_path)

            if text == "":
                for segment in segments:
                    text += segment.text
            output.append(
                f"{file_path}|{output_file_name}|{info.language.upper()}|{text}"
            )
        except:
            logger.error(f"处理文件 {file_path} 失败")
            logger.error(traceback.format_exc())
            print(traceback.format_exc())

    output_folder = output_folder or "output/asr_opt"
    os.makedirs(output_folder, exist_ok=True)
    output_file_path = os.path.abspath(f"{output_folder}/{output_file_name}.list")

    with open(output_file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(output))
        logger.info(f"ASR 任务完成->标注文件路径: {output_file_path}")
    return output_file_path


if __name__ == "__main__":
    output = execute_asr()
    logger.info(output)


############################## 一键三连 ###############################


def preprocess_dataset(
    input_text_path=f"output/asr_opt/{exp_name}/{exp_name}.list",
    input_wav_dir=f"output/slicer_opt/{exp_name}",
    output_dir=f"{exp_root}/{exp_name}",
    bert_pretrained_dir=config.bert_pretrained_dir,
    ssl_pretrained_dir=config.ssl_pretrained_dir,
    pretrained_s2G_path=config.pretrained_s2G_path,
    num_processes=config.num_processes,
    process_index=config.process_index,
    is_half=config.separate_audio_is_half,
):
    """
    Preprocess dataset for GPT-SoVITS training without requiring the webui
    
    Args:
        input_text_path: Path to input text file with format "wav_path|speaker|language|text" per line
        input_wav_dir: Directory containing wav files
        output_dir: Directory to save processed files
        bert_pretrained_dir: Path to BERT pretrained model
        ssl_pretrained_dir: Path to SSL pretrained model 
        pretrained_s2G_path: Path to pretrained s2G model
        num_processes: Number of parallel processes to use
        process_index: Index of current process (0 to num_processes-1)
        is_half: Whether to use half precision
    """

    logger.info("Starting dataset preprocessing...")

    # Create output directories
    os.makedirs(output_dir, exist_ok=True)
    bert_dir = f"{output_dir}/3-bert"
    hubert_dir = f"{output_dir}/4-cnhubert" 
    wav32_dir = f"{output_dir}/5-wav32k"
    os.makedirs(bert_dir, exist_ok=True)
    os.makedirs(hubert_dir, exist_ok=True)
    os.makedirs(wav32_dir, exist_ok=True)
    logger.info(f"Created output directories in {output_dir}")

    # Setup device
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    logger.info(f"Using device: {device}")

    # Helper function to save tensors (handles Chinese paths)
    def my_save(fea, path):
        tmp_path = f"{ttime()}{process_index}.pth"
        torch.save(fea, tmp_path)
        shutil.move(tmp_path, path)

    # 1. Process text and extract BERT features
    def process_text():
        logger.info("Loading BERT model...")
        tokenizer = AutoTokenizer.from_pretrained(bert_pretrained_dir)
        bert_model = AutoModelForMaskedLM.from_pretrained(bert_pretrained_dir)
        if is_half:
            bert_model = bert_model.half()
        bert_model = bert_model.to(device)

        def get_bert_feature(text, word2ph):
            with torch.no_grad():
                inputs = tokenizer(text, return_tensors="pt")
                for i in inputs:
                    inputs[i] = inputs[i].to(device)
                res = bert_model(**inputs, output_hidden_states=True)
                res = torch.cat(res["hidden_states"][-3:-2], -1)[0].cpu()[1:-1]

            phone_level_feature = []
            for i in range(len(word2ph)):
                repeat_feature = res[i].repeat(word2ph[i], 1)
                phone_level_feature.append(repeat_feature)
            return torch.cat(phone_level_feature, dim=0).T

        # Process text lines
        logger.info("Processing text lines...")
        results = []
        with open(input_text_path, "r", encoding="utf8") as f:
            lines = f.read().strip("\n").split("\n")

        language_map = {
            "ZH": "zh", "zh": "zh",
            "JP": "ja", "jp": "ja", "JA": "ja", "ja": "ja",
            "EN": "en", "en": "en", "En": "en"
        }

        for line in lines[process_index::num_processes]:
            try:
                wav_name, spk_name, language, text = line.split("|")
                wav_name = os.path.basename(wav_name)

                if language not in language_map:
                    logger.warning(f"The language={language} of {wav_name} is not supported for training.")
                    continue

                # Clean text and get phonemes
                phones, word2ph, norm_text = clean_text(
                    text.replace("%", "-").replace("￥", ","), 
                    language_map.get(language, language)
                )

                # Extract BERT features for Chinese text
                if language_map.get(language) == "zh":
                    bert_path = f"{bert_dir}/{wav_name}.pt"
                    if not os.path.exists(bert_path):
                        bert_feature = get_bert_feature(norm_text, word2ph)
                        assert bert_feature.shape[-1] == len(phones)
                        my_save(bert_feature, bert_path)

                results.append([wav_name, " ".join(phones), word2ph, norm_text])
            except:
                logger.error(f"Error processing line: {line}")
                logger.error(traceback.format_exc())

        return results

    # 2. Process audio and extract HuBERT features
    def process_audio(wav_names):
        logger.info("Loading HuBERT model...")
        cnhubert.cnhubert_base_path = ssl_pretrained_dir
        model = cnhubert.get_model()
        if is_half:
            model = model.half()
        model = model.to(device)

        maxx = 0.95
        alpha = 0.5
        nan_fails = []

        def process_wav(wav_name):
            hubert_path = f"{hubert_dir}/{wav_name}.pt"
            if os.path.exists(hubert_path):
                return

            wav_path = os.path.join(input_wav_dir, wav_name)
            tmp_audio = load_audio(wav_path, 32000)
            tmp_max = np.abs(tmp_audio).max()

            if tmp_max > 2.2:
                logger.warning(f"{wav_name}-filtered, {tmp_max}")
                return

            # Audio processing
            tmp_audio32 = (tmp_audio / tmp_max * (maxx * alpha * 32768)) + ((1 - alpha) * 32768) * tmp_audio
            tmp_audio32b = (tmp_audio / tmp_max * (maxx * alpha * 1145.14)) + ((1 - alpha) * 1145.14) * tmp_audio
            tmp_audio16k = librosa.resample(tmp_audio32b, orig_sr=32000, target_sr=16000)

            # Extract features
            tensor_wav = torch.from_numpy(tmp_audio16k)
            if is_half:
                tensor_wav = tensor_wav.half()
            tensor_wav = tensor_wav.to(device)

            with torch.no_grad():
                ssl = model.model(tensor_wav.unsqueeze(0))["last_hidden_state"].transpose(1, 2).cpu()

            if np.isnan(ssl.detach().numpy()).sum() != 0:
                nan_fails.append((wav_name, wav_path))
                logger.warning(f"nan filtered: {wav_name}")
                return

            # Save processed audio and features
            wavfile.write(
                f"{wav32_dir}/{wav_name}",
                32000,
                tmp_audio32.astype("int16")
            )
            my_save(ssl, hubert_path)

        logger.info("Processing audio files...")
        for wav_name in wav_names:
            try:
                process_wav(wav_name)
            except:
                logger.error(f"Error processing audio: {wav_name}")
                logger.error(traceback.format_exc())

        # Retry failed files with float32
        if nan_fails and is_half:
            logger.info("Retrying failed files with float32...")
            model = model.float()
            for wav_name, wav_path in nan_fails:
                try:
                    process_wav(wav_name)
                except:
                    logger.error(f"Error processing audio (float32): {wav_name}")
                    logger.error(traceback.format_exc())

    # 3. Generate semantic tokens
    def generate_semantic(wav_names):
        logger.info("Loading VQ model...")
        hps = utils.get_hparams_from_file("GPT_SoVITS/configs/s2.json")
        vq_model = SynthesizerTrn(
            hps.data.filter_length // 2 + 1,
            hps.train.segment_size // hps.data.hop_length,
            n_speakers=hps.data.n_speakers,
            **hps.model
        )

        if is_half:
            vq_model = vq_model.half()
        vq_model = vq_model.to(device)
        vq_model.eval()

        # Load pretrained model
        logger.info("Loading pretrained model weights...")
        print(vq_model.load_state_dict(
            torch.load(pretrained_s2G_path, map_location="cpu")["weight"],
            strict=False
        ))

        logger.info("Generating semantic tokens...")
        semantic_results = []
        for wav_name in wav_names:
            try:
                hubert_path = f"{hubert_dir}/{wav_name}.pt"
                if not os.path.exists(hubert_path):
                    continue

                ssl_content = torch.load(hubert_path, map_location="cpu")
                if is_half:
                    ssl_content = ssl_content.half()
                ssl_content = ssl_content.to(device)

                with torch.no_grad():
                    codes = vq_model.extract_latent(ssl_content)
                semantic = " ".join([str(i) for i in codes[0, 0, :].tolist()])
                semantic_results.append(f"{wav_name}\t{semantic}")
            except:
                logger.error(f"Error generating semantic: {wav_name}")
                logger.error(traceback.format_exc())

        return semantic_results

    # Main processing pipeline
    try:
        # 1. Process text
        logger.info("Starting text processing...")
        text_results = process_text()
        wav_names = [result[0] for result in text_results]

        # Save text results
        text_output = [f"{name}\t{phones}\t{word2ph}\t{norm_text}" 
                      for name, phones, word2ph, norm_text in text_results]
        with open(f"{output_dir}/2-name2text.txt", "w", encoding="utf8") as f:
            f.write("\n".join(text_output) + "\n")
        logger.info("Text processing complete")

        # 2. Process audio
        logger.info("Starting audio processing...")
        process_audio(wav_names)
        logger.info("Audio processing complete")

        # 3. Generate semantic tokens
        logger.info("Starting semantic token generation...")
        semantic_results = generate_semantic(wav_names)
        with open(f"{output_dir}/6-name2semantic.tsv", "w", encoding="utf8") as f:
            f.write("\n".join(semantic_results))
        logger.info("Semantic token generation complete")

        logger.info("Dataset preprocessing completed successfully")
        return True

    except Exception as e:
        logger.error("Error in preprocessing pipeline:")
        logger.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    preprocess_dataset()


############################## 训练SoVITS ###############################


default_batch_size = int(torch.cuda.get_device_properties(0).total_memory / 1024 / 1024 / 1024 + 0.4) // 2

def train_sovits(
    batch_size=config.sovits_batch_size or default_batch_size,
    total_epoch=config.sovits_total_epoch,
    text_low_lr_rate=config.sovits_text_low_lr_rate,
    if_save_latest=config.sovits_if_save_latest,
    if_save_every_weights=config.sovits_if_save_every_weights,
    save_every_epoch=config.sovits_save_every_epoch,
    gpu_numbers=config.sovits_gpu_numbers,
    pretrained_s2G=config.pretrained_s2G_path,
    pretrained_s2D=config.pretrained_s2D_path,
    python_exec=config.python_exec,
    is_half=config.train_sovits_is_half,
    tmp_dir=config.sovits_temp_dir,
    sovits_weight_root=config.sovits_weight_root,
):
    """训练SoVITS模型"""
    try:
        # 1. 读取基础配置
        with open("GPT_SoVITS/configs/s2.json") as f:
            data = json.loads(f.read())

        # 2. 设置输出目录
        s2_dir = f"{exp_root}/{exp_name}"
        os.makedirs(f"{s2_dir}/logs_s2", exist_ok=True)

        # 3. 更新配置
        if not is_half:
            data["train"]["fp16_run"] = False
            batch_size = max(1, batch_size // 2)

        # 更新train部分的配置
        data["train"].update(
            {
                "batch_size": batch_size,
                "epochs": total_epoch,
                "text_low_lr_rate": text_low_lr_rate,
                "pretrained_s2G": pretrained_s2G,
                "pretrained_s2D": pretrained_s2D,
                "if_save_latest": if_save_latest,
                "if_save_every_weights": if_save_every_weights,
                "save_every_epoch": save_every_epoch,
                "gpu_numbers": gpu_numbers,
            }
        )

        # 更新其他配置
        data["data"]["exp_dir"] = s2_dir
        data["s2_ckpt_dir"] = s2_dir
        data["save_weight_dir"] = sovits_weight_root
        data["name"] = exp_name

        # 4. 保存临时配置
        os.makedirs(tmp_dir, exist_ok=True)
        tmp_config_path = f"{tmp_dir}/tmp_s2.json"
        with open(tmp_config_path, "w") as f:
            json.dump(data, f, indent=2)

        # 5. 启动训练
        cmd = f'"{python_exec}" GPT_SoVITS/s2_train.py --config "{tmp_config_path}"'
        print(f"开始训练，执行命令: {cmd}")

        process = Popen(cmd, shell=True)
        process.wait()

        return process.returncode == 0

    except Exception as e:
        print(f"训练过程中出现错误: {str(e)}")
        return False


# 使用示例:
if __name__ == "__main__":
    train_sovits()


############################## 训练GPT ###############################


default_batch_size = int(torch.cuda.get_device_properties(0).total_memory / 1024 / 1024 / 1024 + 0.4) // 2

def train_gpt(
    batch_size=config.gpt_batch_size or default_batch_size,
    total_epoch=config.gpt_total_epoch,
    exp_name=exp_name,
    if_dpo=config.gpt_if_dpo,
    if_save_latest=config.gpt_if_save_latest,
    if_save_every_weights=config.gpt_if_save_every_weights,
    save_every_epoch=config.gpt_save_every_epoch,
    gpu_numbers=config.gpt_gpu_numbers,
    pretrained_s1=config.pretrained_s1_path,
    python_exec=config.python_exec,
    is_half=config.train_gpt_is_half,
    tmp_dir=config.gpt_temp_dir,
    gpt_weight_root=config.gpt_weight_root,
    exp_root=exp_root,
):
    """训练GPT模型"""
    try:
        # 1. 读取基础配置
        with open("GPT_SoVITS/configs/s1longer.yaml") as f:
            data = yaml.safe_load(f)

        # 2. 设置输出目录
        s1_dir = f"{exp_root}/{exp_name}"
        os.makedirs(f"{s1_dir}/logs_s1", exist_ok=True)

        # 3. 更新配置
        if not is_half:
            data["train"]["precision"] = "32"
            batch_size = max(1, batch_size // 2)

        # 更新train部分的配置
        data["train"].update(
            {
                "batch_size": batch_size,
                "epochs": total_epoch,
                "save_every_n_epoch": save_every_epoch,
                "if_save_every_weights": if_save_every_weights,
                "if_save_latest": if_save_latest,
                "if_dpo": if_dpo,
                "half_weights_save_dir": gpt_weight_root,
                "exp_name": exp_name,
            }
        )

        # 更新其他配置
        data.update(
            {
                "pretrained_s1": pretrained_s1,
                "train_semantic_path": f"{s1_dir}/6-name2semantic.tsv",
                "train_phoneme_path": f"{s1_dir}/2-name2text.txt",
                "output_dir": f"{s1_dir}/logs_s1",
            }
        )

        # 4. 设置环境变量
        os.environ.update(
            {"_CUDA_VISIBLE_DEVICES": gpu_numbers.replace("-", ","), "hz": "25hz"}
        )

        # 5. 保存临时配置
        os.makedirs(tmp_dir, exist_ok=True)
        tmp_config_path = f"{tmp_dir}/tmp_s1.yaml"
        with open(tmp_config_path, "w") as f:
            yaml.dump(data, f, default_flow_style=False)

        # 6. 启动训练
        cmd = (
            f'"{python_exec}" GPT_SoVITS/s1_train.py --config_file "{tmp_config_path}"'
        )
        print(f"开始训练，执行命令: {cmd}")

        process = Popen(cmd, shell=True)
        process.wait()

        return process.returncode == 0

    except Exception as e:
        print(f"训练过程中出现错误: {str(e)}")
        return False


# 使用示例:
if __name__ == "__main__":
    success = train_gpt()
