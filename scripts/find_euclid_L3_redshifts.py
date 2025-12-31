import boto3
from botocore import UNSIGNED
from botocore.client import Config

# Verified Bucket
BUCKET_NAME = 'nasa-irsa-euclid-q1'
REGION = 'us-east-1'

s3 = boto3.client('s3', region_name=REGION, config=Config(signature_version=UNSIGNED))

def find_L3_redshifts():
    print(f"-> Probing PHZ L3 Directory for Tile 102018212...")
    
    # 1. Target the L3 directory
    PREFIX_L3 = 'q1/catalogs/PHZ_PF_OUTPUT_FOR_L3/'
    
    # 2. We need to find the subdirectory for our specific Tile
    # Euclid organizes these as .../PHZ_PF_OUTPUT_FOR_L3/<TILE_ID>/...
    target_prefix = f"{PREFIX_L3}102018212/"
    
    print(f"-> Listing files in: {target_prefix}")
    
    try:
        response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=target_prefix)
        
        if 'Contents' in response:
            print(f"-> FOUND REDSHIFT TABLES:")
            for obj in response['Contents']:
                key = obj['Key']
                size_mb = obj['Size'] / 1024**2
                
                # We are looking for the "Physical Parameters" file
                if 'PHYSICAL-PARAMS' in key or 'PHZ' in key:
                    print(f"   [TARGET] {key} ({size_mb:.2f} MB)")
                else:
                    print(f"   {key} ({size_mb:.2f} MB)")
        else:
            print("-> No files found. The Tile ID might be grouped differently.")
            print("-> Attempting to list base directory to check structure...")
            base_resp = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=PREFIX_L3, Delimiter='/')
            if 'CommonPrefixes' in base_resp:
                print("-> Available Tile Directories (First 5):")
                for p in base_resp['CommonPrefixes'][:5]:
                    print(f"   - {p['Prefix']}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_L3_redshifts()
