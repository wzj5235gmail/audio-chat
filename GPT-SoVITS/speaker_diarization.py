import os
os.environ['KMP_DUPLICATE_LIB_OK']='TRUE'

from pyannote.audio import Pipeline
from pydub import AudioSegment
import torch
import argparse

pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    use_auth_token=os.getenv("HUGGINGFACE_TOKEN"))

# send pipeline to GPU (when available)
pipeline.to(torch.device("cuda"))

def process_audio(audio_path, output_dir):
    # apply pretrained pipeline
    diarization = pipeline(audio_path)

    # Extract audio segment for each speaker turn
    audio = AudioSegment.from_wav(audio_path)

    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Export each segment
    segment_number = 0
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        print(f"start={turn.start:.1f}s stop={turn.end:.1f}s speaker_{speaker}")
        start_ms = int(turn.start * 1000)
        end_ms = int(turn.end * 1000)
        segment = audio[start_ms:end_ms]

        # Save segment
        if end_ms - start_ms >= 1000:
            output_path = os.path.join(
                output_dir, f"{speaker}_segment_{segment_number}.wav"
            )
            segment.export(output_path, format="wav")
            segment_number += 1

def main():
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='音频说话人分离程序')
    parser.add_argument('exp_name', type=str, help='实验名称')
    
    # 获取 exp_name 参数
    args, _ = parser.parse_known_args()
    exp_name = args.exp_name
    
    # 重新添加其他参数
    parser.add_argument('--audio_path', type=str, 
                       default=f"output/uvr5_vocal/{exp_name}/vocal_{exp_name}.wav_10.wav", 
                       help='输入音频文件的路径')
    parser.add_argument(
        "--output_dir",
        type=str,
        default=f"output/slicer_opt/{exp_name}",
        help=f"输出目录路径 (默认: output/slicer_opt/{exp_name})",
    )

    # 解析所有命令行参数
    args = parser.parse_args()

    # 处理音频
    process_audio(args.audio_path, args.output_dir)

if __name__ == "__main__":
    main()
