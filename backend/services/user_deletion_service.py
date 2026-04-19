from bson import ObjectId

from backend.db import DatabaseManager
from backend.logger import logger
from backend.services.blob_service import BlobStorageService


async def hard_delete_user(user_id: str):
    """
    Performs a cascade hard-delete of a user.
    1. Deletes all document extraction records in Mongo (where created_by_user_id == user_id).
    2. Deletes all blobs in Azure Storage under the user prefix.
    3. Deletes the user profile in Mongo.
    """
    db = DatabaseManager.get_db()

    logger.info(f"Initiating hard-delete for user: {user_id}")

    # Try both ObjectId and str for matching
    try:
        user_oid = ObjectId(user_id)
    except Exception:
        user_oid = user_id

    query = {"_id": user_oid}
    # Also support string match if ObjectId conversion succeeded but we want to be safe
    # However, usually it's one or the other.

    # 1. Delete Extraction Records
    # Using both str and OID for safety in foreign keys
    await db.documents.delete_many({"created_by_user_id": user_id})
    doc_res = await db.documents.delete_many({"created_by_user_id": user_oid})
    logger.info(f"Deleted extraction records for user {user_id}")

    # 2. Delete Blobs
    await BlobStorageService.delete_user_blobs(user_id)
    logger.info(f"Deleted blobs for user {user_id}")

    # 3. Delete User Profile
    user_res = await db.users.delete_one(query)
    if user_res.deleted_count == 0:
        logger.warning(
            f"User {user_id} not found during profile deletion step")
    else:
        logger.info(f"User profile {user_id} deleted successfully")

    return {
        "user_id": user_id,
        "extraction_records_deleted": doc_res.deleted_count,
        "profile_deleted": user_res.deleted_count > 0
    }


async def bulk_hard_delete_users(user_ids: list[str]):
    """
    Deletes multiple users in a loop.
    Returns results for each.
    """
    results = []
    for uid in user_ids:
        try:
            res = await hard_delete_user(uid)
            results.append(res)
        except Exception as e:
            logger.error(f"Failed to bulk delete user {uid}: {e}")
            results.append({
                "user_id": uid,
                "error": str(e),
                "profile_deleted": False
            })

    return {
        "total_attempted": len(user_ids),
        "deleted_count": sum(1 for r in results if r.get("profile_deleted")),
        "details": results
    }
