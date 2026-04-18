import logging

import aiosqlite
from fastapi import APIRouter, HTTPException

from backend.db import get_db_connection
from backend.schemas.taxpayer_schema import (TaxpayerCreateRequest,
                                               TaxpayerLinkAadharRequest)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/taxpayers", tags=["Taxpayers"])


@router.post("/", status_code=201)
async def create_taxpayer(req: TaxpayerCreateRequest):
    async with get_db_connection() as db:
        try:
            await db.execute('''
                INSERT INTO taxpayers (
                    pan_number, first_name, middle_name, last_name, dob, father_name
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                req.pan_number, req.first_name, req.middle_name, req.last_name,
                req.dob.isoformat() if req.dob else None, req.father_name
            ))
            await db.commit()
            return {"status": "success", "message": "Taxpayer created successfully", "pan_number": req.pan_number}
        except aiosqlite.IntegrityError:
            raise HTTPException(status_code=400, detail="Taxpayer with this PAN already exists")
        except Exception:
            logger.exception("Failed to create taxpayer")
            raise HTTPException(status_code=500, detail="Internal server error")


@router.patch("/{pan_number}")
async def link_aadhar(pan_number: str, req: TaxpayerLinkAadharRequest):
    async with get_db_connection() as db:
        # Check if taxpayer exists
        async with db.execute('SELECT 1 FROM taxpayers WHERE pan_number = ?', (pan_number,)) as cursor:
            if not await cursor.fetchone():
                raise HTTPException(status_code=404, detail="Taxpayer not found")

        # Link Aadhar
        try:
            await db.execute('''
                UPDATE taxpayers
                SET aadhar_number = ?, gender = ?, address_line = ?, pincode = ?
                WHERE pan_number = ?
            ''', (
                req.aadhar_number, req.gender, req.address_line, req.pincode, pan_number
            ))
            await db.commit()
            return {"status": "success", "message": "Aadhar linked successfully"}
        except Exception:
            logger.exception("Failed to link Aadhar")
            raise HTTPException(status_code=500, detail="Internal server error")

