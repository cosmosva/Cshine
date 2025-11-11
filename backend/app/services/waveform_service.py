"""
音频波形提取服务
用于从音频文件中提取波形数据，用于前端可视化
"""

import os
import tempfile
import librosa
import numpy as np
from loguru import logger
from typing import List


class WaveformService:
    """音频波形提取服务"""
    
    @staticmethod
    def extract_waveform(audio_path: str, num_points: int = 800) -> List[float]:
        """
        从音频文件中提取波形数据
        
        Args:
            audio_path: 音频文件路径（本地路径或URL）
            num_points: 需要提取的波形点数（默认800个点，足够前端绘制）
            
        Returns:
            归一化后的波形数据数组，值在 0-1 之间
        """
        try:
            logger.info(f"开始提取音频波形: {audio_path}")
            
            # 加载音频文件
            # sr=16000 降采样到16kHz，减少计算量
            # mono=True 转换为单声道
            y, sr = librosa.load(audio_path, sr=16000, mono=True)
            
            logger.info(f"音频加载成功: 采样率={sr}, 长度={len(y)}")
            
            # 计算每个采样点应该包含的音频样本数
            samples_per_point = len(y) // num_points
            
            if samples_per_point == 0:
                # 音频太短，直接返回原始数据
                waveform = [abs(float(sample)) for sample in y[:num_points]]
            else:
                # 提取波形数据
                waveform = []
                for i in range(num_points):
                    start = i * samples_per_point
                    end = start + samples_per_point
                    
                    # 防止越界
                    if end > len(y):
                        end = len(y)
                    
                    segment = y[start:end]
                    
                    # 使用 RMS（均方根）作为振幅表示
                    # RMS 能更好地反映音频的能量和响度
                    if len(segment) > 0:
                        amplitude = np.sqrt(np.mean(segment**2))
                        waveform.append(float(amplitude))
            
            # 归一化到 0-1 范围
            max_amp = max(waveform) if waveform else 1.0
            if max_amp > 0:
                waveform = [w / max_amp for w in waveform]
            
            logger.info(f"波形提取成功: {len(waveform)} 个数据点")
            
            return waveform
            
        except Exception as e:
            logger.error(f"提取音频波形失败: {e}")
            raise Exception(f"波形提取失败: {str(e)}")
    
    @staticmethod
    def extract_waveform_from_url(audio_url: str, num_points: int = 800) -> List[float]:
        """
        从远程URL提取音频波形
        
        Args:
            audio_url: 音频文件URL（如OSS地址）
            num_points: 需要提取的波形点数
            
        Returns:
            归一化后的波形数据数组
        """
        try:
            import requests
            
            logger.info(f"从URL下载音频: {audio_url}")
            
            # 下载音频文件到临时目录
            response = requests.get(audio_url, timeout=60)
            response.raise_for_status()
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix='.m4a') as tmp_file:
                tmp_file.write(response.content)
                tmp_path = tmp_file.name
            
            try:
                # 提取波形
                waveform = WaveformService.extract_waveform(tmp_path, num_points)
                return waveform
            finally:
                # 删除临时文件
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                    logger.info(f"已删除临时文件: {tmp_path}")
                    
        except Exception as e:
            logger.error(f"从URL提取波形失败: {e}")
            raise Exception(f"从URL提取波形失败: {str(e)}")

