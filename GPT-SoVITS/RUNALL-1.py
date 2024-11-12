import logging
import traceback
import os, sys, numpy as np
import subprocess
import torch
import shutil
from scipy.io import wavfile
from tools.my_utils import load_audio
from slicer2 import Slicer
import RUNALL_CONFIG as config

# 设置日志
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

exp_root = "logs"
exp_name = getattr(config, "exp_name", "Suou_Yuki")
video_path = getattr(config, "video_path", r"C:\Users\Administrator\Downloads\mai-2.mp4")
input_path = f"training_data/{exp_name}.wav"

############################## 视频转为音频 #############################

if not video_path.endswith(".wav"):
    logger.info(f"开始处理视频文件: {video_path}")
    subprocess.run(["ffmpeg.exe", "-i", video_path, "-ac", "1", "-ar", "32000", "-f", "wav", input_path])
    logger.info(f"视频处理完成")
else:
    logger.info(f"源文件已为音频文件: {video_path}")
    shutil.copy2(video_path, input_path)

############################## 分离人声和伴奏 ###############################

# 从配置文件读取参数
device = getattr(config, "device", "cuda:0")  # 默认使用 cuda:0
is_half = getattr(config, "separate_audio_is_half", True)  # 默认使用半精度
model_name = getattr(config, "uvr5_model", "HP5_only_main_vocal")  # 默认使用 HP5
agg = getattr(config, "uvr5_agg", 10)  # 默认激进程度为10
output_format = getattr(config, "output_format", "wav")  # 默认输出格式为wav

def separate_audio(
    input_path,  # 输入音频文件路径
    model_name=model_name,  # 使用配置文件中的模型名称
    output_vocal=f"output/uvr5_vocal/{exp_name}",  # 人声输出路径
    output_inst=f"output/uvr5_inst/{exp_name}",  # 伴奏输出路径
    agg=agg,  # 使用配置文件中的激进程度
    format=output_format,  # 使用配置文件中的输出格式
):
    # 导入必要的类
    from vr import AudioPre, AudioPreDeEcho
    from mdxnet import MDXNetDereverb

    logger.info(f"开始处理音频文件: {input_path}")
    logger.info(f"使用模型: {model_name}")

    try:
        # 选择预处理函数
        if model_name == "onnx_dereverb_By_FoxJoy":
            logger.info("使用 MDXNetDereverb 模型")
            pre_fun = MDXNetDereverb(15)
        else:
            func = AudioPre if "DeEcho" not in model_name else AudioPreDeEcho
            logger.info(
                f"使用{'AudioPre' if 'DeEcho' not in model_name else 'AudioPreDeEcho'}模型"
            )
            pre_fun = func(
                agg=int(agg),
                model_path=f"tools/uvr5/uvr5_weights/{model_name}.pth",
                device=device,
                is_half=is_half == "True",
            )

        # 处理音频
        logger.info("开始音频处理...")
        pre_fun._path_audio_(
            input_path,
            output_inst,  # 伴奏输出目录
            output_vocal,  # 人声输出目录
            format,
        )
        logger.info("音频处理完成")

        # 清理资源
        logger.info("清理模型资源...")
        if model_name == "onnx_dereverb_By_FoxJoy":
            del pre_fun.pred.model
            del pre_fun.pred.model_
        else:
            del pre_fun.model
            del pre_fun

        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            logger.info("CUDA缓存已清理")

        return True, "处理成功"

    except Exception as e:
        logger.error(f"处理失败: {str(e)}")
        logger.error(traceback.format_exc())
        return False, f"处理失败: {str(e)}"


############################## 说话人分离 ###############################

def run_speaker_diarization(exp_name):
    logger.info("开始说话人分离处理...")
    try:
        # 从配置文件读取conda环境名称
        conda_env = getattr(config, "conda_env", "pyannote")
        
        # 激活 conda 环境
        activate_cmd = f"conda activate {conda_env}"
        diarization_cmd = f"python speaker_diarization.py {exp_name}"
        
        # Windows 上需要使用 'conda run' 来执行命令
        if os.name == 'nt':  # Windows
            activate_cmd = f"conda run -n {conda_env} python speaker_diarization.py {exp_name}"
            subprocess.run(activate_cmd, shell=True, check=True)
        else:  # Linux/Mac
            # 使用 source 激活环境并运行命令
            cmd = f"source activate {conda_env} && python speaker_diarization.py {exp_name}"
            subprocess.run(cmd, shell=True, check=True, executable='/bin/bash')
            
        logger.info("说话人分离处理完成")
        return True, "说话人分离处理成功"
        
    except subprocess.CalledProcessError as e:
        logger.error(f"说话人分离处理失败: {str(e)}")
        return False, f"说话人分离处理失败: {str(e)}"
    except Exception as e:
        logger.error(f"发生未知错误: {str(e)}")
        logger.error(traceback.format_exc())
        return False, f"处理失败: {str(e)}"

if __name__ == "__main__":
    # Run previous steps first
    success, message = separate_audio(input_path=input_path)
    logger.info(message)

    # Run speaker diarization
    success, message = run_speaker_diarization(exp_name)
    logger.info(message)
