import boto3
from botocore import UNSIGNED
from botocore.client import Config

# 1. Verified Bucket Details from IRSA Documentation
BUCKET_NAME = 'nasa-irsa-euclid-q1'  #
REGION = 'us-east-1'                 #

# Configure S3 client for anonymous access (Public Data)
s3 = boto3.client('s3', region_name=REGION,
                  config=Config(signature_version=UNSIGNED))

def list_euclid_files():
    print(f"-> Connecting to IRSA Cloud ({BUCKET_NAME})...")
    try:
        # 2. Probe the 'q1/MER' prefix for Level 2 Mosaics
        PREFIX_MER = 'q1/MER/'
        print(f"-> Probing '{PREFIX_MER}' for Deep Field Mosaics...")
        
        response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=PREFIX_MER, MaxKeys=10)
        
        if 'Contents' in response:
            print("-> Connection Successful. Found Mosaic Data:")
            for obj in response['Contents']:
                # Show file key and size in MB
                key = obj['Key']
                size_mb = obj['Size'] / 1024**2
                print(f"   - {key} ({size_mb:.2f} MB)")
        else:
            print("-> Connected, but no files found in MER prefix.")

        # 3. Probe the 'q1/catalogs' prefix for Source Tables
        PREFIX_CAT = 'q1/catalogs/'
        print(f"\n-> Probing '{PREFIX_CAT}' for Photometric/Spectroscopic Catalogs...")
        
        cat_response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=PREFIX_CAT, MaxKeys=5)
        if 'Contents' in cat_response:
             for obj in cat_response['Contents']:
                print(f"   - {obj['Key']} ({obj['Size'] / 1024**2:.2f} MB)")

    except Exception as e:
        print(f"-> Connection Failed: {e}")

if __name__ == "__main__":
    list_euclid_files()
