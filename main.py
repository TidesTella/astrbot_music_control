from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.api import AstrBotConfig
import aiohttp
import json
import urllib.parse
import webbrowser

@register("astrbot_music_control", "RC-CHN", "音乐播放器控制插件，支持播放/暂停/切歌/音量调节/搜索/收藏等", "0.2")
class MusicControlPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config
        music_config = config.get("music_api", {})
        self.session = aiohttp.ClientSession(trust_env=True)
        self.base_url = music_config.get("base_url", "").rstrip('/')
        self.default_filter = music_config.get("default_filter", "status,name,singer,albumName,lyricLineText,duration,progress,playbackRate")
    # ================== 核心业务逻辑 ==================
    async def _get_status_text(self) -> str:
        if not self.base_url:
            return "错误：音乐API基础URL未配置。"
        url = f"{self.base_url}/status?filter={self.default_filter}"
        try:
            async with self.session.get(url) as resp:
                data = await resp.json()
                status = data.get('status', 'unknown')
                name = data.get('name', '未知')
                singer = data.get('singer', '未知')
                progress = data.get('progress', 0)
                duration = data.get('duration', 0)
                volume = data.get('volume', 0)
                progress_str = f"{int(progress//60)}:{int(progress%60):02d}"
                duration_str = f"{int(duration//60)}:{int(duration%60):02d}"
                status_map = {
                    'playing': '正在播放',
                    'paused': '已暂停',
                    'stoped': '已停止',
                    'error': '出现错误'
                }
                return (f"{status_map.get(status, status)}\n"
                        f"{name} - {singer}\n"
                        f"{progress_str} / {duration_str}\n"
                        f"音量: {volume}%")
        except Exception as e:
            logger.error(f"获取状态失败: {e}")
            return f"获取音乐状态失败: {str(e)}"

    async def _search_and_play(self, keyword: str, play_later: bool = False) -> str:
        if not keyword:
            return "请提供搜索关键词。"
        
        encoded_keyword = urllib.parse.quote(keyword)
        if play_later:
            scheme_url = f"lxmusic://music/searchPlay/{encoded_keyword}?playLater=true"
        else:
            scheme_url = f"lxmusic://music/searchPlay/{encoded_keyword}"
        
        try:
            webbrowser.open(scheme_url)
            if play_later:
                return f"已将 '{keyword}' 加入稍后播放列表\n（请确保洛雪音乐助手正在运行）"
            else:
                return f"正在播放: {keyword}\n（如果播放器未响应，请确保洛雪音乐助手已运行并启用 Scheme URL 支持）"
        except Exception as e:
            logger.error(f"唤起 Scheme URL 失败: {e}")
            return f"播放失败: {str(e)}\n请确保洛雪音乐助手正在运行。"

    async def _play(self) -> str:
        if not self.base_url:
            return "错误：音乐API基础URL未配置。"
        try:
            async with self.session.post(f"{self.base_url}/play") as resp:
                return "已继续播放" if resp.status == 200 else f"播放失败 (HTTP {resp.status})"
        except Exception as e:
            return f"请求失败: {str(e)}"

    async def _pause(self) -> str:
        if not self.base_url:
            return "错误：音乐API基础URL未配置。"
        try:
            async with self.session.post(f"{self.base_url}/pause") as resp:
                return "已暂停播放" if resp.status == 200 else f"暂停失败 (HTTP {resp.status})"
        except Exception as e:
            return f"请求失败: {str(e)}"

    async def _next(self) -> str:
        if not self.base_url:
            return "错误：音乐API基础URL未配置。"
        try:
            async with self.session.post(f"{self.base_url}/skip-next") as resp:
                return "已切换到下一曲" if resp.status == 200 else f"切换失败 (HTTP {resp.status})"
        except Exception as e:
            return f"请求失败: {str(e)}"

    async def _prev(self) -> str:
        if not self.base_url:
            return "错误：音乐API基础URL未配置。"
        try:
            async with self.session.post(f"{self.base_url}/skip-prev") as resp:
                return "已切换到上一曲" if resp.status == 200 else f"切换失败 (HTTP {resp.status})"
        except Exception as e:
            return f"请求失败: {str(e)}"

    async def _volume(self, volume: int) -> str:
        if not self.base_url:
            return "错误：音乐API基础URL未配置。"
        if volume < 0 or volume > 100:
            return "音量值必须在 1-100 之间"
        try:
            async with self.session.post(f"{self.base_url}/volume?volume={volume}") as resp:
                return f"音量已调整为 {volume}%" if resp.status == 200 else f"调整失败 (HTTP {resp.status})"
        except Exception as e:
            return f"请求失败: {str(e)}"

    async def _seek(self, offset: int) -> str:
        if not self.base_url:
            return "错误：音乐API基础URL未配置。"
        if offset < 0:
            return "时间不能为负数"
        try:
            async with self.session.post(f"{self.base_url}/seek?offset={offset}") as resp:
                if resp.status == 200:
                    minutes = offset // 60
                    seconds = offset % 60
                    return f"已跳转到 {minutes}分{seconds}秒"
                else:
                    return f"跳转失败 (HTTP {resp.status})"
        except Exception as e:
            return f"请求失败: {str(e)}"

    async def _collect(self) -> str:
        if not self.base_url:
            return "错误：音乐API基础URL未配置。"
        try:
            async with self.session.post(f"{self.base_url}/collect") as resp:
                return "已收藏当前歌曲" if resp.status == 200 else f"收藏失败 (HTTP {resp.status})"
        except Exception as e:
            return f"请求失败: {str(e)}"

    async def _uncollect(self) -> str:
        if not self.base_url:
            return "错误：音乐API基础URL未配置。"
        try:
            async with self.session.post(f"{self.base_url}/uncollect") as resp:
                return "已取消收藏" if resp.status == 200 else f"取消收藏失败 (HTTP {resp.status})"
        except Exception as e:
            return f"请求失败: {str(e)}"

    # ================== LLM 工具（由AI 调用） ==================
    @filter.llm_tool(name="get_music_status")
    async def get_music_status(self, event: AstrMessageEvent) -> str:
        '''获取当前音乐播放器的状态（歌曲名、艺术家、进度、音量等）'''
        return await self._get_status_text()

    @filter.llm_tool(name="music_play")
    async def music_play(self, event: AstrMessageEvent) -> str:
        '''继续播放当前选中的歌曲'''
        return await self._play()

    @filter.llm_tool(name="music_pause")
    async def music_pause(self, event: AstrMessageEvent) -> str:
        '''暂停当前播放的歌曲'''
        return await self._pause()

    @filter.llm_tool(name="music_next")
    async def music_next(self, event: AstrMessageEvent) -> str:
        '''切换到下一首歌曲'''
        return await self._next()

    @filter.llm_tool(name="music_prev")
    async def music_prev(self, event: AstrMessageEvent) -> str:
        '''切换到上一首歌曲'''
        return await self._prev()

    @filter.llm_tool(name="music_volume")
    async def music_volume(self, event: AstrMessageEvent, volume: int) -> str:
        '''调整音乐播放器音量
        Args:
            volume (int): 音量值，范围 1-100
        '''
        return await self._volume(volume)

    @filter.llm_tool(name="music_seek")
    async def music_seek(self, event: AstrMessageEvent, offset: int) -> str:
        '''跳转到歌曲的指定位置
        Args:
            offset (int): 跳转时间，单位：秒
        '''
        return await self._seek(offset)

    @filter.llm_tool(name="music_search")
    async def music_search(self, event: AstrMessageEvent, keyword: str) -> str:
        '''搜索歌曲（使用 Scheme URL 唤起播放器）
        Args:
            keyword (str): 搜索关键词，如歌曲名或歌手名
        '''
        encoded_keyword = urllib.parse.quote(keyword)
        scheme_url = f"lxmusic://music/search/{encoded_keyword}"
        try:
            webbrowser.open(scheme_url)
            return f"已在音乐播放器中搜索: {keyword}\n（请查看洛雪音乐助手窗口）"
        except Exception as e:
            logger.error(f"唤起 Scheme URL 搜索失败: {e}")
            return f"搜索失败: {str(e)}\n请确保洛雪音乐助手正在运行。"

    @filter.llm_tool(name="music_search_play")
    async def music_search_play(self, event: AstrMessageEvent, keyword: str) -> str:
        '''搜索并播放歌曲（使用 Scheme URL 唤起播放器）
        Args:
            keyword (str): 歌曲名，如"反乌托邦 栖云"
        '''
        return await self._search_and_play(keyword, play_later=False)

    @filter.llm_tool(name="music_collect")
    async def music_collect(self, event: AstrMessageEvent) -> str:
        '''收藏当前播放的歌曲'''
        return await self._collect()

    @filter.llm_tool(name="music_uncollect")
    async def music_uncollect(self, event: AstrMessageEvent) -> str:
        '''取消收藏当前播放的歌曲'''
        return await self._uncollect()

    # ================== 命令控制（使用 command_group） ==================
    @filter.command_group("music")
    def music(self) -> None:
        """音乐控制命令组"""

    @music.command("status")
    async def status_cmd(self, event: AstrMessageEvent):
        """获取当前播放状态"""
        result = await self._get_status_text()
        yield event.plain_result(result)

    @music.command("play")
    async def play_cmd(self, event: AstrMessageEvent, keyword: str = None):
        """
        继续播放（无参数），或搜索并播放歌曲（带参数）
        示例：/music play 反乌托邦
        """
        if keyword:
            result = await self._search_and_play(keyword, play_later=False)
        else:
            result = await self._play()
        yield event.plain_result(result)

    @music.command("playnext")
    async def playnext_cmd(self, event: AstrMessageEvent, keyword: str):
        """
        搜索并加入稍后播放列表
        示例：/music playnext 反乌托邦
        """
        result = await self._search_and_play(keyword, play_later=True)
        yield event.plain_result(result)

    @music.command("pause")
    async def pause_cmd(self, event: AstrMessageEvent):
        """暂停当前播放"""
        result = await self._pause()
        yield event.plain_result(result)

    @music.command("next")
    async def next_cmd(self, event: AstrMessageEvent):
        """切换到下一曲"""
        result = await self._next()
        yield event.plain_result(result)

    @music.command("prev")
    async def prev_cmd(self, event: AstrMessageEvent):
        """切换到上一曲"""
        result = await self._prev()
        yield event.plain_result(result)

    @music.command("volume")
    async def volume_cmd(self, event: AstrMessageEvent, volume: int):
        """
        调整音量，范围 1-100
        示例：/music volume 50
        """
        result = await self._volume(volume)
        yield event.plain_result(result)

    @music.command("seek")
    async def seek_cmd(self, event: AstrMessageEvent, offset: int):
        """
        跳转进度，单位秒
        示例：/music seek 90（跳转到1分30秒）
        """
        result = await self._seek(offset)
        yield event.plain_result(result)

    @music.command("search")
    async def search_cmd(self, event: AstrMessageEvent, keyword: str):
        """
        搜索歌曲（使用 Scheme URL 唤起播放器）
        示例：/music search 反乌托邦
        """
        encoded_keyword = urllib.parse.quote(keyword)
        scheme_url = f"lxmusic://music/search/{encoded_keyword}"
        try:
            webbrowser.open(scheme_url)
            yield event.plain_result(f"已在音乐播放器中搜索: {keyword}\n（请查看洛雪音乐助手窗口）")
        except Exception as e:
            logger.error(f"唤起 Scheme URL 搜索失败: {e}")
            yield event.plain_result(f"搜索失败: {str(e)}\n请确保洛雪音乐助手正在运行。")

    @music.command("collect")
    async def collect_cmd(self, event: AstrMessageEvent):
        """收藏当前歌曲"""
        result = await self._collect()
        yield event.plain_result(result)

    @music.command("uncollect")
    async def uncollect_cmd(self, event: AstrMessageEvent):
        """取消收藏当前歌曲"""
        result = await self._uncollect()
        yield event.plain_result(result)

    # ================== 资源清理 ==================
    async def terminate(self):
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("MusicControlPlugin: HTTP session closed.")
