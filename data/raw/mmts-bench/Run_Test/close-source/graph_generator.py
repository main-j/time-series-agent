import pandas as pd
import matplotlib.pyplot as plt
import base64
import io
import os
import ast
import logging
from datetime import datetime
from tqdm import tqdm

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TimeSeriesImagePreprocessor:
    def __init__(self, csv_path: str, output_dir: str = None):
        """
        Initialize time series image preprocessor
        
        Args:
            csv_path: Path to CSV file
            output_dir: Output directory, if None uses same directory as CSV file
        """
        self.csv_path = csv_path
        
        if output_dir is None:
            csv_dir = os.path.dirname(csv_path)
            self.output_dir = csv_dir
        else:
            self.output_dir = output_dir
        
        self.graph_dir = os.path.join(self.output_dir, "graph")
        os.makedirs(self.graph_dir, exist_ok=True)
        
        base_name = os.path.splitext(os.path.basename(csv_path))[0]
        self.output_csv_path = os.path.join(self.output_dir, f"{base_name}_with_base64.csv")
        
        logger.info(f"CSV file: {self.csv_path}")
        logger.info(f"Graph save directory: {self.graph_dir}")
        logger.info(f"Output CSV: {self.output_csv_path}")

    def create_time_series_image(self, value_list, row_idx):
        """
        Create time series image and return base64 encoding, also save image file
        
        Args:
            value_list: Time series data list
            row_idx: Row index for generating filename
            
        Returns:
            str: Base64 encoded image data
        """
        try:
            if len(value_list) > 8:
                num_channels = 1
            else:
                num_channels = len(value_list)
            
            width_inches = 15.0
            height_per_channel = 3.2
            total_height = height_per_channel * num_channels
            
            plt.figure(figsize=(width_inches, total_height), dpi=100)
            
            if num_channels == 1:
                plt.plot(range(len(value_list)), value_list, 'b-', linewidth=1.5)
                plt.title('Time Series', fontsize=12)
                plt.xlabel('Time Index', fontsize=10)
                plt.ylabel('Value', fontsize=10)
                plt.grid(True, alpha=0.3)
                plt.xlim(0, len(value_list) - 1)
            else:
                for i, channel_data in enumerate(value_list):
                    plt.subplot(num_channels, 1, i + 1)
                    plt.plot(range(len(channel_data)), channel_data, 'b-', linewidth=1.5)
                    plt.title(f'Time Series {i+1}', fontsize=10)
                    plt.xlabel('Time Index', fontsize=8)
                    plt.ylabel('Value', fontsize=8)
                    plt.grid(True, alpha=0.3)
                    plt.xlim(0, len(channel_data) - 1)
            
            plt.tight_layout()
            
            filename = f"timeseries_row_{row_idx:04d}.png"
            filepath = os.path.join(self.graph_dir, filename)
            
            plt.savefig(filepath, format='png', bbox_inches='tight', pad_inches=0.1, dpi=100)
            
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight', pad_inches=0.1, dpi=100)
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return image_base64, filename
            
        except Exception as e:
            logger.error(f"Failed to generate image (row {row_idx}): {e}")
            plt.close()
            return "", ""

    def process_csv(self):
        """
        Process CSV file, generate images and base64 data for each row
        """
        try:
            logger.info("Reading CSV file...")
            df = pd.read_csv(self.csv_path)
            logger.info(f"Successfully read CSV file, {len(df)} rows in total")
            
            if 'value' not in df.columns:
                raise ValueError("Missing 'value' column in CSV file")
            
            df['image_base64'] = ''
            df['image_filename'] = ''
            
            success_count = 0
            error_count = 0
            
            logger.info("Starting image generation...")
            for idx in tqdm(range(len(df)), desc="Image generation progress"):
                try:
                    value_str = str(df.iloc[idx]['value'])
                    value_list = ast.literal_eval(value_str)
                    
                    image_base64, filename = self.create_time_series_image(value_list, idx)
                    
                    if image_base64 and filename:
                        df.at[idx, 'image_base64'] = image_base64
                        df.at[idx, 'image_filename'] = filename
                        success_count += 1
                    else:
                        error_count += 1
                        logger.warning(f"Failed to generate image for row {idx}")
                        
                except Exception as e:
                    error_count += 1
                    logger.error(f"Error processing row {idx}: {e}")
                    continue
            
            logger.info("Saving processed CSV file...")
            df.to_csv(self.output_csv_path, index=False, encoding='utf-8')
            
            logger.info("=== Processing Complete ===")
            logger.info(f"Total rows: {len(df)}")
            logger.info(f"Successfully generated images: {success_count}")
            logger.info(f"Failed: {error_count}")
            logger.info(f"Success rate: {success_count/len(df)*100:.1f}%")
            logger.info(f"Images saved to: {self.graph_dir}")
            logger.info(f"Processed CSV file: {self.output_csv_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error occurred while processing CSV file: {e}")
            return False

    def verify_results(self):
        """
        Verify processing results
        """
        try:
            if not os.path.exists(self.output_csv_path):
                logger.error("Output CSV file does not exist")
                return False
            
            df = pd.read_csv(self.output_csv_path)
            
            if 'image_base64' not in df.columns or 'image_filename' not in df.columns:
                logger.error("Missing new columns in output CSV file")
                return False
            
            valid_base64 = df['image_base64'].notna() & (df['image_base64'] != '')
            valid_filename = df['image_filename'].notna() & (df['image_filename'] != '')
            
            base64_count = valid_base64.sum()
            filename_count = valid_filename.sum()
            
            logger.info("=== Verification Results ===")
            logger.info(f"Valid base64 data: {base64_count}/{len(df)}")
            logger.info(f"Valid filenames: {filename_count}/{len(df)}")
            
            existing_files = 0
            for filename in df[valid_filename]['image_filename']:
                filepath = os.path.join(self.graph_dir, filename)
                if os.path.exists(filepath):
                    existing_files += 1
            
            logger.info(f"Existing image files: {existing_files}/{filename_count}")
            
            if base64_count == len(df) and filename_count == len(df) and existing_files == filename_count:
                logger.info("All data processed and verified successfully")
                return True
            else:
                logger.warning("Some data processing incomplete")
                return False
                
        except Exception as e:
            logger.error(f"Error occurred during verification: {e}")
            return False

def main():
    """
    Main function
    """
    CSV_PATH = "/path/to/your/dataset.csv"
    OUTPUT_DIR = "/path/to/output/directory"
    
    logger.info("=== Time Series Image Preprocessor ===")
    logger.info(f"Input file: {CSV_PATH}")
    
    if not os.path.exists(CSV_PATH):
        logger.error(f"Input file does not exist: {CSV_PATH}")
        return
    
    preprocessor = TimeSeriesImagePreprocessor(csv_path=CSV_PATH, output_dir=OUTPUT_DIR)
    
    start_time = datetime.now()
    success = preprocessor.process_csv()
    end_time = datetime.now()
    
    if success:
        logger.info(f"Processing time: {end_time - start_time}")
        
        logger.info("Verifying processing results...")
        preprocessor.verify_results()
    else:
        logger.error("Processing failed")

if __name__ == "__main__":
    main()