import ibm_boto3
from ibm_botocore.client import Config, ClientError

def delete_item(bucket_name, item_name,ressource):
    ressource.Object(bucket_name, item_name).delete()
    return item_name+" in "+bucket_name+" deleted"

def create_bucket(bucket_name,ressource):
       ressource.Bucket(bucket_name).create(
            CreateBucketConfiguration={
                "LocationConstraint":"eu-de-standard "
            }
        )

def create_json_file(bucket_name, item_name, json, ressource):
        ressource.Object(bucket_name, item_name).put(
            Body=json
        )

def get_buckets(ressource):
        buckets = ressource.buckets.all()
        val = []
        for bucket in buckets:
           val.appedn(bucket.name)
        return val

def get_bucket_contents(bucket_name,ressource):
    files = ressource.Bucket(bucket_name).objects.all()
    val = []
    for file in files:
        val.append(file.key)
    return val

def get_item(bucket_name, item_name,ressource):
    file = ressource.Object(bucket_name, item_name).get()
    return file

def delete_item(bucket_name, item_name,ressource):
    ressource.Object(bucket_name, item_name).delete()
    return item_name+" deleted"

def delete_bucket(bucket_name,ressource):
    ressource.Bucket(bucket_name).delete()
    print(bucket_name+" deleted")
