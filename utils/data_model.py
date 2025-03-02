from typing import (Any, Dict, NamedTuple, Optional)
from pydantic import BaseModel


class ApiResultHandler(BaseModel):
    """
    API返回的数据处理器
    """
    content: Dict[str, Any]
    """API返回的JSON对象序列化以后的Dict对象"""
    data: Optional[Dict[str, Any]] = None
    """API返回的数据体"""
    message: str = ""
    """API返回的消息内容"""
    status: Optional[int] = None
    """API返回的状态码"""

    def __init__(self, content: Dict[str, Any]):
        super().__init__(content=content)

        for key in ["data", "entity"]:
            if self.data is None:
                self.data = self.content.get(key)
            else:
                break

        for key in ["code", "status"]:
            if self.status is None:
                self.status = self.content.get(key)

        for key in ["desc", "message"]:
            if self.message == "":
                self.message = self.content.get(key, "")

    @property
    def success(self):
        """
        是否成功
        """
        return self.status in [0, 200] or self.message in ["成功", "OK", "success"]


class LoginResultHandler(ApiResultHandler):
    """
    登录API返回的数据处理器
    """
    pwd: Optional[int] = None
    """登录状态"""
    location: Optional[str] = None
    """登录成功后的跳转地址"""

    def __init__(self, content: Dict[str, Any]):
        super().__init__(content=content)

        self.pwd = self.content.get("pwd")
        self.location = self.content.get("location")

    @property
    def need_captcha(self):
        """
        是否需要验证码
        """
        return self.status == 87001 or "验证码" in self.message

    @property
    def pwd_wrong(self):
        """
        密码错误
        """
        return self.status == 70016


class DailyTasksResult(NamedTuple):
    """
    每日任务API返回的数据处理器
    """
    name: str
    """任务名称"""
    showType: bool
    """任务状态"""
    desc: Optional[str]
    """任务描述"""


class SignResultHandler(ApiResultHandler):
    """
    签到API返回的数据处理器
    """

    growth: Optional[str] = None
    """签到成功后的成长值"""

    def __init__(self, content: Dict[str, Any]):
        super().__init__(content=content)
        
        self.growth = self.content.get("entity", {})
        if type(self.growth) == dict:
            self.growth = self.growth.get("score", "未知")
        elif type(self.growth) == int:
            self.growth = str(self.growth)
        

    def __bool__(self):
        """
        签到是否成功
        """
        return self.success

    @property
    def ck_invalid(self):
        """
        cookie是否失效
        """
        return self.status == 401


class TokenResultHandler(ApiResultHandler):
    """
    TOKEN数据处理器
    """
    token: str = ""

    def __init__(self, content: Dict[str, Any]):
        super().__init__(content=content)

        self.token = self.data.get("token", "")

    @property
    def need_verify(self):
        """需要验证码"""
        return self.data.get("result") == False and self.data.get("url")

    @property
    def success(self):
        """是否成功获取TOKEN"""
        return self.token != ""
    
class GeetestResult(NamedTuple):
    """人机验证结果数据"""
    validate: str
    challenge: str
    
