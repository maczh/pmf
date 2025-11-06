import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
from db.mongoClient import mongo
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from bson import ObjectId
import json

@dataclass
class ImageInfo:
    imageUrl: Optional[str] = None
    scale16Vs9Url: Optional[str] = None
    scale1Vs1Url: Optional[str] = None
    scale4Vs3Url: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ImageInfo":
        if not data:
            return cls()
        return cls(
            imageUrl=data.get("imageUrl"),
            scale16Vs9Url=data.get("scale16Vs9Url"),
            scale1Vs1Url=data.get("scale1Vs1Url"),
            scale4Vs3Url=data.get("scale4Vs3Url"),
        )


@dataclass
class DishSku:
    skuId: Optional[str] = None
    specName: Optional[str] = None
    defaultSkuFlag: Optional[str] = None
    sellPrice: Optional[int] = None
    barCode: Optional[str] = None
    required: Optional[bool] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DishSku":
        if not data:
            return cls()
        return cls(
            skuId=data.get("skuId"),
            specName=data.get("specName"),
            defaultSkuFlag=data.get("defaultSkuFlag"),
            sellPrice=data.get("sellPrice"),
            barCode=data.get("barCode"),
            required=data.get("required"),
        )


@dataclass
class ComboGroupDetail:
    singleDishId: Optional[str] = None
    sort: Optional[int] = None
    maxChoose: Optional[int] = None
    minChoose: Optional[int] = None
    fixChoose: Optional[int] = None
    dishSkuId: Optional[str] = None
    dishSkuPrice: Optional[int] = None
    optType: Optional[str] = None
    defaultFlag: Optional[str] = None
    dishName: Optional[str] = None
    specName: Optional[str] = None
    sellPrice: Optional[int] = None
    dishImageInfoList: List[ImageInfo] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ComboGroupDetail":
        if not data:
            return cls()
        imgs = data.get("dishImageInfoList") or []
        return cls(
            singleDishId=data.get("singleDishId"),
            sort=data.get("sort"),
            maxChoose=data.get("maxChoose"),
            minChoose=data.get("minChoose"),
            fixChoose=data.get("fixChoose"),
            dishSkuId=data.get("dishSkuId"),
            dishSkuPrice=data.get("dishSkuPrice"),
            optType=data.get("optType"),
            defaultFlag=data.get("defaultFlag"),
            dishName=data.get("dishName"),
            specName=data.get("specName"),
            sellPrice=data.get("sellPrice"),
            dishImageInfoList=[ImageInfo.from_dict(i) for i in imgs],
        )


@dataclass
class ComboGroup:
    groupName: Optional[str] = None
    maxChoose: Optional[int] = None
    minChoose: Optional[int] = None
    sort: Optional[int] = None
    repeatable: Optional[str] = None
    comboGroupDetailList: List[ComboGroupDetail] = field(default_factory=list)
    groupType: Optional[str] = None
    groupId: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ComboGroup":
        if not data:
            return cls()
        details = data.get("comboGroupDetailList") or []
        return cls(
            groupName=data.get("groupName"),
            maxChoose=data.get("maxChoose"),
            minChoose=data.get("minChoose"),
            sort=data.get("sort"),
            repeatable=data.get("repeatable"),
            comboGroupDetailList=[ComboGroupDetail.from_dict(d) for d in details],
            groupType=data.get("groupType"),
            groupId=data.get("groupId"),
        )


@dataclass
class Dish:
    _id: Optional[ObjectId] = None
    dishId: Optional[str] = None
    dishName: Optional[str] = None
    dishType: Optional[str] = None
    categoryId: Optional[str] = None
    categoryName: Optional[str] = None
    hiddenOnMiniProgram: Optional[bool] = None
    dishSkuList: List[DishSku] = field(default_factory=list)
    unitName: Optional[str] = None
    tags: Optional[Any] = None
    helpCode: Optional[str] = None
    comboGroupList: List[ComboGroup] = field(default_factory=list)
    cookingWayGroupList: Optional[Any] = None
    state: Optional[str] = None
    startNumber: Optional[int] = None
    startInterval: Optional[int] = None
    modifyPriceFlag: Optional[str] = None
    discountFlag: Optional[str] = None
    orderSingleFlag: Optional[str] = None
    dishImageUrlList: Optional[Any] = None
    spicyLevel: Optional[int] = None
    sort: Optional[int] = None
    dishStockInfoList: Optional[Any] = None
    unitId: Optional[str] = None
    dishImageInfoList: List[ImageInfo] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Dish":
        if not data:
            return cls()
        sku_list = data.get("dishSkuList") or []
        combo_list = data.get("comboGroupList") or []
        img_list = data.get("dishImageInfoList") or []
        return cls(
            _id=data.get("_id"),
            dishId=data.get("dishId"),
            dishName=data.get("dishName"),
            dishType=data.get("dishType"),
            categoryId=data.get("categoryId"),
            categoryName=data.get("categoryName"),
            hiddenOnMiniProgram=data.get("hiddenOnMiniProgram"),
            dishSkuList=[DishSku.from_dict(s) for s in sku_list],
            unitName=data.get("unitName"),
            tags=data.get("tags"),
            helpCode=data.get("helpCode"),
            comboGroupList=[ComboGroup.from_dict(g) for g in combo_list],
            cookingWayGroupList=data.get("cookingWayGroupList"),
            state=data.get("state"),
            startNumber=data.get("startNumber"),
            startInterval=data.get("startInterval"),
            modifyPriceFlag=data.get("modifyPriceFlag"),
            discountFlag=data.get("discountFlag"),
            orderSingleFlag=data.get("orderSingleFlag"),
            dishImageUrlList=data.get("dishImageUrlList"),
            spicyLevel=data.get("spicyLevel"),
            sort=data.get("sort"),
            dishStockInfoList=data.get("dishStockInfoList"),
            unitId=data.get("unitId"),
            dishImageInfoList=[ImageInfo.from_dict(i) for i in img_list],
        )
        
if __name__ == "__main__":
    # 示例用法
    mongo_local = mongo(
        uri="mongodb://jihai:Voodoo#123456@127.0.0.1:27017/jihai",
        db_name="jihai",
        pool_size=5,
        max_overflow=10,
    )
    # mongo_dev = mongo(
    #     uri="mongodb://ququmandev:rXie4kYIrGb#@dds-bp1cbd6ebff4b8441789-pub.mongodb.rds.aliyuncs.com:3717,dds-bp1cbd6ebff4b8442273-pub.mongodb.rds.aliyuncs.com:3717/dev",
    #     db_name="dev",
    #     pool_size=5,
    #     max_overflow=10,
    #     )

    # 获取集合
    # collection_dev = mongo_dev.get_collection("dish_44576219")
    collection_local = mongo_local.get_collection("dish_44576219")

    # 查询示例
    documents = collection_local.find_one({"dishId" : "837556731007"})
    print(json.dumps(documents, default=str, indent=2,ensure_ascii=False))
    # for doc in documents:
    #     dish = Dish.from_dict(doc)
    #     print(json.dumps(dish.comboGroupList[0],default=str, indent=2,ensure_ascii=False))
    #     collection_local.insert_one(doc)

#     data = {
#     "dishId" : "833400541007",
#     "dishName" : "福佳白啤酒248ML",
#     "dishType" : "SINGLE",
#     "categoryId" : "151928331007",
#     "categoryName" : "酒水",
#     "hiddenOnMiniProgram" : False,
#     "dishSkuList" : [ 
#         {
#             "skuId" : "864102801007",
#             "specName" : "标准",
#             "defaultSkuFlag" : "N",
#             "sellPrice" : 800,
#             "barCode" : "864102801007",
#             "required" : False
#         }
#     ],
#     "unitName" : "瓶",
#     "tags" : None,
#     "helpCode" : "fjb248ML",
#     "comboGroupList" : None,
#     "cookingWayGroupList" : None,
#     "state" : "ONLINE",
#     "startNumber" : 1,
#     "startInterval" : 1,
#     "modifyPriceFlag" : "N",
#     "discountFlag" : "N",
#     "orderSingleFlag" : "Y",
#     "dishImageUrlList" : None,
#     "spicyLevel" : 0,
#     "sort" : 1,
#     "dishStockInfoList" : None,
#     "unitId" : "200751091007",
#     "dishImageInfoList" : [ 
#         {
#             "imageUrl" : "https://cube.elemecdn.com/5/6e/e652848c3548a3cdf23359eb1fd64jpg.jpg",
#             "scale16Vs9Url" : "https://cube.elemecdn.com/5/6e/e652848c3548a3cdf23359eb1fd64jpg.jpg",
#             "scale1Vs1Url" : "https://cube.elemecdn.com/5/6e/e652848c3548a3cdf23359eb1fd64jpg.jpg",
#             "scale4Vs3Url" : "https://s.koubei.com/j2GQjZ77pfNEkfc5pZzirPbPMF.jpeg"
#         }
#     ]
# }

    # doc = Dish.from_dict(data)
    # collection_local.insert_one(data)

    # 关闭连接
    # mongo_dev.close()
    mongo_local.close()