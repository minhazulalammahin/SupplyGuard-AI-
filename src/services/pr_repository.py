"""Purchase Request loader and repository using Pandas."""
from decimal import Decimal
from pathlib import Path
from typing import Dict, Optional
import pandas as pd
from src.models.schemas import PurchaseRequestItem
from src.config import PURCHASE_REQUEST_PATH


class PurchaseRequestRepository:
    """Loads and provides access to baseline Purchase Request items."""
    
    def __init__(self, csv_path: str | Path = PURCHASE_REQUEST_PATH):
        self.csv_path = Path(csv_path)
        self._items: Dict[str, PurchaseRequestItem] = {}
        self._load()

    def _load(self) -> None:
        if not self.csv_path.exists():
            raise FileNotFoundError(f"Purchase request file not found at: {self.csv_path}")
            
        df = pd.read_csv(self.csv_path)
        for _, row in df.iterrows():
            item_code = str(row["Item"]).strip()
            pr_item = PurchaseRequestItem(
                pr_number=str(row["PR number"]).strip(),
                item_code=item_code,
                description=str(row["Description"]).strip(),
                unit=str(row["Unit"]).strip(),
                quantity_requested=Decimal(str(row["Quantity requested"])),
                maximum_unit_price=Decimal(str(row["Maximum unit price (BDT)"]))
            )
            self._items[item_code] = pr_item

    def get_item(self, item_code: str) -> Optional[PurchaseRequestItem]:
        """Retrieve a PR item by item code (e.g. 'A', 'B', 'C', 'D', 'E')."""
        return self._items.get(item_code.strip())

    def get_all_items(self) -> Dict[str, PurchaseRequestItem]:
        """Get all PR items mapped by item code."""
        return self._items

