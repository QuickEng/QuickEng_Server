from pydantic import BaseModel, Field
from typing import List

# =========================================================
# 1. [요청] 앱이 서버에게 보낼 때 ("이 영상 분석해줘!")
# =========================================================
class AnalyzeRequest(BaseModel):
    # -----------------------------------------------------
    # 파이썬 변수명: video_url  (우리가 코드 짤 때 편한 이름)
    # 앱이 보낼 이름: videoUrl  (앱 개발자가 편한 이름)
    # Field(..., alias="...") : "내 진짜 이름은 이건데, 밖에서는 저 별명을 써!"
    # -----------------------------------------------------
    video_url: str = Field(..., alias="videoUrl")
    
    # 기본값은 "ko"(한국어)이고, 앱에서는 "targetLang"이라는 이름표를 달고 들어옴
    target_lang: str = Field("ko", alias="targetLang")

    class Config:
        # [설정] 별명(videoUrl)으로 들어와도 받고, 본명(video_url)으로 들어와도 받아준다.
        populate_by_name = True

# =========================================================
# 2. [내부 부품] 단어 카드 하나하나의 모양
# =========================================================
class WordItem(BaseModel):
    # 카드의 고유 id
    id: str

    # 이건 둘 다 똑같이 "expression"을 쓰니까 별명 설정 불필요
    expression: str
    
    # 파이썬: meaning_kr <---> 앱: meaningKr
    meaning_kr: str = Field(..., alias="meaningKr")
    
    # 파이썬: context_tag <---> 앱: contextTag
    context_tag: str = Field(..., alias="contextTag")
    

    class Config:
        populate_by_name = True


# =========================================================
# 3. [응답] 서버가 앱에게 줄 때 ("자, 여기 분석 결과야!")
# =========================================================
class AnalyzeResponse(BaseModel):
    video_id: str = Field(..., alias="videoId")
    title: str
    #thumbnail_url: str = Field(..., alias="thumbnailUrl")
    
    # ★ 핵심 수정: 명세서의 scriptItems에는 단어장(WordItem)이 들어갑니다.
    script_items: List[WordItem] = Field(..., alias="scriptItems")

    class Config:
        populate_by_name = True

