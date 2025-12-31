import boto3
from botocore import UNSIGNED
from botocore.client import Config

BUCKET_NAME = 'nasa-irsa-euclid-q1'
REGION = 'us-east-1'

s3 = boto3.client('s3', region_name=REGION, config=Config(signature_version=UNSIGNED))

def find_redshift_catalogs():
    print(f"-> Searching for PHZ (Photo-Z) Catalogs in {BUCKET_NAME}...")
    
    # 1. Check the Tile Directory specifically for PHZ files
    # We know Tile 102018212 exists, let's look at EVERYTHING in its folder
    prefix_tile = 'q1/catalogs/MER_FINAL_CATALOG/102018212/'
    print(f"\n-> Listing all files in Tile 102018212 ({prefix_tile})...")
    
    try:
        response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix_tile)
        found_phz = False
        if 'Contents' in response:
            for obj in response['Contents']:
                key = obj['Key']
                # Look for PHZ, Z, or PHOT keywords
                if 'PHZ' in key or 'Z-CAT' in key or 'PHOT' in key:
                    print(f"   [CANDIDATE] {key} ({obj['Size']/1024**2:.2f} MB)")
                    found_phz = True
                else:
                    print(f"   {key}")
        
        if not found_phz:
            print("   -> No explicit PHZ file found in this folder.")
            
            # 2. Check for a dedicated PHZ top-level directory
            print("\n-> Checking for parallel 'PHZ' directory...")
            top_level = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix='q1/catalogs/', Delimiter='/')
            if 'CommonPrefixes' in top_level:
                for p in top_level['CommonPrefixes']:
                    print(f"   - {p['Prefix']}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_redshift_catalogs()
