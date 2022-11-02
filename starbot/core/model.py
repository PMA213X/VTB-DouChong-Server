import time
from enum import Enum
from typing import List, Optional, Any

from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, At, AtAll, Image
from pydantic import BaseModel, PrivateAttr


class LiveOn(BaseModel):
    """
    开播推送配置
    可使用构造方法手动传入所需的各项配置
    或使用 LiveOn.default() 获取功能全部开启的默认配置
    """

    DEFAULT_MESSAGE: Optional[str] = "{uname} 正在直播 {title}\n{url}{next}{cover}"
    """默认消息模板"""

    enabled: Optional[bool] = False
    """是否启用开播推送。默认：False"""

    at_all: Optional[bool] = False
    """是否 @全体成员。默认：False"""

    message: Optional[str] = ""
    """
    开播推送内容模板。
    可用占位符：{uname}主播昵称，{title}直播间标题，{url}直播间链接，{cover}直播间封面图，{next}消息分条。
    默认：""
    """

    @classmethod
    def default(cls):
        """
        获取功能全部开启的默认 LiveOn 实例
        默认配置：启用开播推送，启用 @全体成员，推送内容模板为 "{uname} 正在直播 {title}\n{url}{next}{cover}"
        """
        return LiveOn(enabled=True, at_all=True, message=LiveOn.DEFAULT_MESSAGE)

    def __str__(self):
        return f"启用: {self.enabled}\n@全体: {self.at_all}\n推送内容:\n{self.message}"


class LiveOff(BaseModel):
    """
    下播推送配置
    可使用构造方法手动传入所需的各项配置
    或使用 LiveOff.default() 获取功能全部开启的默认配置
    """

    DEFAULT_MESSAGE: Optional[str] = "{uname} 直播结束了\n{time}{next}{danmu_count}{danmu_mvp}{box_profit}"
    """默认消息模板"""

    enabled: Optional[bool] = False
    """是否启用下播推送。默认：False"""

    message: Optional[str] = ""
    """
    下播推送内容模板。
    可用占位符：{uname}主播昵称，{time}本次直播时长，{danmu_count}弹幕总数，{danmu_mvp}弹幕MVP，{box_profit}宝盒盈亏，{next}消息分条。
    默认：""
    """

    @classmethod
    def default(cls):
        """
        获取功能全部开启的默认 LiveOff 实例
        默认配置：启用下播推送，推送内容模板为 "{uname} 直播结束了\n{time}{next}{danmu_count}{danmu_mvp}{box_profit}"
        """
        return LiveOff(enabled=True, message=LiveOff.DEFAULT_MESSAGE)

    def __str__(self):
        return f"启用: {self.enabled}\n推送内容:\n{self.message}"


class LiveReport(BaseModel):
    """
    直播报告配置，直播报告会在下播推送后发出，下播推送是否开启不会影响直播报告的推送
    可使用构造方法手动传入所需的各项配置
    或使用 LiveReport.default() 获取功能全部开启的默认配置
    """

    enabled: Optional[bool] = False
    """是否启用直播报告。默认：False"""

    danmu_cloud: Optional[bool] = False
    """是否生成弹幕词云。默认：False"""

    @classmethod
    def default(cls):
        """
        获取功能全部开启的默认 LiveReport 实例
        默认配置：启用直播报告，生成弹幕词云
        """
        return LiveReport(enabled=True, danmu_cloud=True)

    def __str__(self):
        return f"启用: {self.enabled}\n生成弹幕词云: {self.danmu_cloud}"


class DynamicUpdate(BaseModel):
    """
    动态推送配置
    可使用构造方法手动传入所需的各项配置
    或使用 DynamicUpdate.default() 获取功能全部开启的默认配置
    """

    DEFAULT_MESSAGE: Optional[str] = "{uname} {action}\n{url}"
    """默认消息模板"""

    enabled: Optional[bool] = False
    """是否启用动态推送。默认：False"""

    message: Optional[str] = ""
    """
    动态推送内容模板。
    可用占位符：{uname}主播昵称，{action}动态操作类型（发表了新动态，转发了新动态，投稿了新视频...），{url}动态链接（若为发表视频、专栏等则为视频、专栏等对应的链接）。
    默认：""
    """

    @classmethod
    def default(cls):
        """
        获取功能全部开启的默认 DynamicUpdate 实例
        默认配置：启用动态推送，推送内容模板为 "{uname} {action}\n{url}"
        """
        return DynamicUpdate(enabled=True, message=DynamicUpdate.DEFAULT_MESSAGE)

    def __str__(self):
        return f"启用: {self.enabled}\n推送内容:\n{self.message}"


class PushType(Enum):
    """
    推送目标 PushTarget 所对应推送类型

    推送类型，0 为私聊推送，1 为群聊推送
    + Friend : 0
    + Group  : 1
    """
    Friend = 0
    Group = 1


class PushTarget(BaseModel):
    """
    需要推送的推送目标，可选 QQ 好友或 QQ 群推送
    可额外使用推送 Key 将推送姬扩展至其他业务，通过调用 HTTP API 进行消息推送
    """

    id: int
    """QQ 号或群号"""

    type: Optional[PushType] = PushType.Group
    """推送类型，可选 QQ 好友或 QQ 群推送。默认：PushType.Group"""

    live_on: Optional[LiveOn] = LiveOn()
    """开播推送配置。默认：LiveOn()"""

    live_off: Optional[LiveOff] = LiveOff()
    """下播推送配置。默认：LiveOff()"""

    live_report: Optional[LiveReport] = LiveReport()
    """直播报告配置。默认：LiveReport()"""

    dynamic_update: Optional[DynamicUpdate] = DynamicUpdate()
    """动态推送配置。默认：DynamicUpdate()"""

    key: Optional[str] = None
    """推送 Key，可选功能，可使用此 Key 通过 HTTP API 向对应的好友或群推送消息。默认：str(id)"""

    def __init__(self, **data: Any):
        super().__init__(**data)
        if not self.key:
            self.key = "-".join([str(self.id), str(self.type.value)])

    def __eq__(self, other):
        if isinstance(other, PushTarget):
            return self.id == other.id and self.type == other.type
        return False

    def __hash__(self):
        return hash(self.key)


class Message(BaseModel):
    """
    消息封装类
    """

    id: int
    """目标 QQ 号或目标群号"""

    content: str
    """原始消息内容，可包含 {next}、{atall} 等占位符"""

    type: Optional[PushType] = PushType.Group
    """发送目标类型，PushType.Friend 为私聊消息，PushType.Group 为群聊消息。默认：PushType.Group"""

    __time: Optional[int] = PrivateAttr()
    """消息创建时间戳"""

    __chains: Optional[List[MessageChain]] = PrivateAttr()
    """原始消息内容自动处理后的消息链列表"""

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.__time = int(time.time())
        self.__chains = Message.gen_message_chains(self.content)

    def get_time(self) -> int:
        return self.__time

    def get_message_chains(self) -> List[MessageChain]:
        return self.__chains

    @classmethod
    def gen_message_chains(cls, raw_msg: str) -> List[MessageChain]:
        """
        转换 {next}，{atall}，{at}，{pic_url}，{pic_path} 元素，将原始消息内容转换为可发送的消息链

        Args:
            raw_msg: 原始消息文本

        Returns:
            可直接发送的消息链列表
        """
        chains = []

        raw_msgs = raw_msg.split("{next}")
        for msg in raw_msgs:
            chain = MessageChain([])
            next_code = msg.find("{")
            while msg != "":
                if next_code == -1:
                    chain.append(Plain(msg))
                    msg = ""
                elif next_code != 0:
                    chain.append(Plain(msg[:next_code]))
                    msg = msg[next_code:]
                    next_code = msg.find("{")
                else:
                    code_end = msg.find("}")
                    if code_end == -1:
                        chain.append(Plain(msg))
                        msg = ""
                    else:
                        if msg[1:3] == "at":
                            at_target = msg[3:code_end]
                            if at_target == "all":
                                chain.append(AtAll())
                            elif at_target.isdigit():
                                chain.append((At(int(at_target))))
                                chain.append(Plain(" "))
                            else:
                                chain.append(Plain("[无效的@参数]"))
                        elif msg[1:7] == "urlpic":
                            pic_url = msg[8:code_end]
                            if pic_url != "":
                                chain.append(Image(url=pic_url))
                        elif msg[1:8] == "pathpic":
                            pic_path = msg[9:code_end]
                            if pic_path != "":
                                chain.append(Image(path=pic_path))
                        else:
                            chain.append(Plain(msg[:code_end + 1]))
                        msg = msg[code_end + 1:]
                        next_code = msg.find("{")
            chains.append(chain)

            return chains
