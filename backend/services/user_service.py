import logging
from datetime import datetime
from typing import List, Optional

from backend.db import DatabaseManager
from backend.schemas.user_schema import (UserCreateRequest, 
                                        UserLinkAadharRequest, 
                                        UserResponse)

logger = logging.getLogger(__name__)

async def create_or_update_user(req: UserCreateRequest) -> UserResponse:
    """
    Upserts a user based on PAN number.
    """
    async with DatabaseManager.get_db() as db:
        now = datetime.now().isoformat()
        
        await db.execute('''
            INSERT INTO users (pan_number, full_name, dob, father_name, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(pan_number) DO UPDATE SET
                full_name = excluded.full_name,
                dob = excluded.dob,
                father_name = excluded.father_name,
                updated_at = excluded.updated_at
        ''', (
            req.pan_number, 
            req.full_name, 
            req.dob.isoformat() if req.dob else None, 
            req.father_name,
            now
        ))
        await db.commit()
        
        return await get_user_by_pan(req.pan_number)

async def link_aadhar(pan_number: str, req: UserLinkAadharRequest) -> UserResponse:
    """
    Links Aadhar data to user.
    """
    async with DatabaseManager.get_db() as db:
        now = datetime.now().isoformat()
        
        user = await get_user_by_pan(pan_number)
        if not user:
            raise ValueError(f"User with PAN {pan_number} not found")
            
        await db.execute('''
            UPDATE users
            SET aadhar_number = ?, gender = ?, address_line = ?, pincode = ?, updated_at = ?
            WHERE pan_number = ?
        ''', (
            req.aadhar_number, 
            req.gender, 
            req.address_line, 
            req.pincode, 
            now,
            pan_number
        ))
        await db.commit()
        
        return await get_user_by_pan(pan_number)

async def get_user_by_pan(pan_number: str) -> Optional[UserResponse]:
    async with DatabaseManager.get_db() as db:
        async with db.execute('SELECT * FROM users WHERE pan_number = ?', (pan_number,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return UserResponse.model_validate(dict(row))
    return None

async def list_all_users() -> List[UserResponse]:
    async with DatabaseManager.get_db() as db:
        async with db.execute('SELECT * FROM users ORDER BY created_at DESC') as cursor:
            rows = await cursor.fetchall()
            return [UserResponse.model_validate(dict(row)) for row in rows]
