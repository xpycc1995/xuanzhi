"""
选址合理性分析Agent - 基于AutoGen (新版 autogen-agentchat API)

负责生成规划选址论证报告的第4章"建设项目选址合理性分析"。
"""

import os
from typing import Dict, Any, Optional
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient

from src.models.rationality_data import RationalityData
from src.utils.logger import logger


class RationalityAnalysisAgent:
    """
    选址合理性分析Agent
    
    使用AutoGen的AssistantAgent，专门负责生成第4章"选址合理性分析"内容。
    
    该Agent需要处理以下内容：
    - 环境影响分析（大气、噪声、水、固废、交通、生态修复）
    - 压覆矿产资源情况分析
    - 地质灾害影响分析
    - 社会稳定影响分析（合法性风险、生活环境风险、社会环境风险）
    - 节能分析
    - 选址合理性分析小结
    """
    
    def __init__(
        self,
        model_client: OpenAIChatCompletionClient,
        prompt_template_path: str = None
    ):
        """
        初始化选址合理性分析Agent
        
        Args:
            model_client: OpenAIChatCompletionClient 实例
            prompt_template_path: 提示词模板路径，默认为templates/prompts/rationality_analysis.md
        """
        self.model_client = model_client
        
        # 设置默认提示词模板路径
        if prompt_template_path is None:
            # 获取项目根目录
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            prompt_template_path = os.path.join(
                project_root,
                "templates",
                "prompts",
                "rationality_analysis.md"
            )
        
        # 加载system_message
        self.system_message = self._load_system_message(prompt_template_path)
        self.template_path = prompt_template_path
        
        # 创建AutoGen AssistantAgent
        self.agent = AssistantAgent(
            name="rationality_analysis_agent",
            model_client=self.model_client,
            system_message=self.system_message,
            description="负责生成规划选址论证报告第4章'建设项目选址合理性分析'的专业AI Agent"
        )
        
        logger.info(f"选址合理性分析Agent初始化完成")
        logger.info(f"  提示词模板: {prompt_template_path}")
    
    def _load_system_message(self, template_path: str) -> str:
        """
        加载提示词模板作为system_message
        
        Args:
            template_path: 提示词模板文件路径
            
        Returns:
            system_message字符串
        """
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                system_message = f.read()
            
            logger.info(f"提示词模板加载成功 ({len(system_message)} 字符)")
            return system_message
        
        except FileNotFoundError:
            raise FileNotFoundError(
                f"提示词模板文件不存在: {template_path}\n"
                f"请确保模板文件存在于正确位置。"
            )
        except Exception as e:
            raise RuntimeError(f"加载提示词模板失败: {str(e)}")
    
    def _validate_data(self, data: RationalityData):
        """
        验证输入数据
        
        Args:
            data: 选址合理性分析数据
            
        Raises:
            ValueError: 数据验证失败
        """
        # Pydantic已经做了基本验证，这里做业务逻辑验证
        if not data.项目基本信息:
            raise ValueError("项目基本信息不能为空")
        
        if not data.合理性结论:
            raise ValueError("合理性结论不能为空")
        
        logger.info("数据验证通过")
    
    def _build_user_message(
        self,
        rationality_data: RationalityData,
        context: str = None
    ) -> str:
        """
        构建发送给Agent的用户消息
        
        Args:
            rationality_data: 选址合理性分析数据
            context: 可选的上下文信息
            
        Returns:
            格式化的用户消息字符串
        """
        lines = []
        
        # 添加上下文信息（如果有）
        if context:
            lines.append("# 前置章节摘要")
            lines.append(context)
            lines.append("")
        
        # 添加项目基本信息
        lines.append("# 项目基本信息")
        for key, value in rationality_data.项目基本信息.items():
            lines.append(f"- {key}：{value}")
        
        # 添加环境影响分析
        lines.append("\n# 环境影响分析")
        env = rationality_data.环境影响分析
        
        ## 大气环境影响
        lines.append("\n## 大气环境影响")
        lines.append(f"- 影响程度：{env.大气环境影响.影响程度}")
        lines.append(f"- 施工期扬尘措施：")
        for i, measure in enumerate(env.大气环境影响.施工期扬尘措施, 1):
            lines.append(f"  {i}. {measure}")
        if env.大气环境影响.施工机械废气措施:
            lines.append(f"- 施工机械废气措施：")
            for i, measure in enumerate(env.大气环境影响.施工机械废气措施, 1):
                lines.append(f"  {i}. {measure}")
        if env.大气环境影响.运营期废气措施:
            lines.append(f"- 运营期废气措施：")
            for i, measure in enumerate(env.大气环境影响.运营期废气措施, 1):
                lines.append(f"  {i}. {measure}")
        lines.append(f"- 防治结论：{env.大气环境影响.防治结论}")
        
        ## 噪声环境影响
        lines.append("\n## 噪声环境影响")
        lines.append(f"- 影响程度：{env.噪声环境影响.影响程度}")
        lines.append(f"- 施工期噪声措施：")
        for i, measure in enumerate(env.噪声环境影响.施工期噪声措施, 1):
            lines.append(f"  {i}. {measure}")
        lines.append(f"- 防治结论：{env.噪声环境影响.防治结论}")
        
        ## 水环境影响
        lines.append("\n## 水环境影响")
        lines.append(f"- 影响程度：{env.水环境影响.影响程度}")
        lines.append(f"- 施工期废水措施：")
        for i, measure in enumerate(env.水环境影响.施工期废水措施, 1):
            lines.append(f"  {i}. {measure}")
        lines.append(f"- 运营期废水措施：")
        for i, measure in enumerate(env.水环境影响.运营期废水措施, 1):
            lines.append(f"  {i}. {measure}")
        lines.append(f"- 防治结论：{env.水环境影响.防治结论}")
        
        ## 固体废弃物影响
        lines.append("\n## 固体废弃物影响")
        lines.append(f"- 影响程度：{env.固体废弃物影响.影响程度}")
        lines.append(f"- 施工期固废措施：")
        for i, measure in enumerate(env.固体废弃物影响.施工期固废措施, 1):
            lines.append(f"  {i}. {measure}")
        lines.append(f"- 防治结论：{env.固体废弃物影响.防治结论}")
        
        ## 交通影响
        lines.append("\n## 交通影响")
        lines.append(f"- 施工期交通影响：{env.交通影响.施工期交通影响}")
        lines.append(f"- 施工期缓解措施：")
        for i, measure in enumerate(env.交通影响.施工期缓解措施, 1):
            lines.append(f"  {i}. {measure}")
        lines.append(f"- 防治结论：{env.交通影响.防治结论}")
        
        ## 生态修复
        lines.append("\n## 生态修复措施")
        lines.append(f"- 对居民点影响：{env.生态修复.对居民点影响}")
        lines.append(f"- 居民点防治措施：")
        for i, measure in enumerate(env.生态修复.居民点防治措施, 1):
            lines.append(f"  {i}. {measure}")
        lines.append(f"- 对动物影响：{env.生态修复.对动物影响}")
        lines.append(f"- 动物防治措施：")
        for i, measure in enumerate(env.生态修复.动物防治措施, 1):
            lines.append(f"  {i}. {measure}")
        lines.append(f"- 对植物影响：{env.生态修复.对植物影响}")
        lines.append(f"- 植物防治措施：")
        for i, measure in enumerate(env.生态修复.植物防治措施, 1):
            lines.append(f"  {i}. {measure}")
        lines.append(f"- 水土保持措施：")
        for i, measure in enumerate(env.生态修复.水土保持措施, 1):
            lines.append(f"  {i}. {measure}")
        lines.append(f"- 环境影响小结：{env.环境影响小结}")
        
        # 添加压覆矿产资源情况
        lines.append("\n# 压覆矿产资源情况")
        mineral = rationality_data.矿产资源压覆
        lines.append(f"- 是否压覆矿产资源：{'是' if mineral.是否压覆矿产资源 else '否'}")
        lines.append(f"- 是否与采矿权重叠：{'是' if mineral.是否与采矿权重叠 else '否'}")
        lines.append(f"- 是否与探矿权重叠：{'是' if mineral.是否与探矿权重叠 else '否'}")
        lines.append(f"- 是否与地质项目重叠：{'是' if mineral.是否与地质项目重叠 else '否'}")
        if mineral.复函信息:
            lines.append(f"- 复函信息：{mineral.复函信息}")
        lines.append(f"- 分析结论：{mineral.分析结论}")
        
        # 添加地质灾害影响分析
        lines.append("\n# 地质灾害影响分析")
        geo = rationality_data.地质灾害分析
        lines.append(f"- 地质灾害类型：{', '.join(geo.地质灾害类型) if geo.地质灾害类型 else '无'}")
        lines.append(f"- 地质灾害易发程度：{geo.地质灾害易发程度}")
        lines.append(f"- 危险性等级：{geo.危险性等级}")
        lines.append(f"- 地震基本烈度：{geo.地震基本烈度}")
        if geo.地震动峰值加速度:
            lines.append(f"- 地震动峰值加速度：{geo.地震动峰值加速度}")
        lines.append(f"- 防治措施：")
        for i, measure in enumerate(geo.防治措施, 1):
            lines.append(f"  {i}. {measure}")
        lines.append(f"- 分析结论：{geo.分析结论}")
        
        # 添加社会稳定影响分析
        lines.append("\n# 社会稳定影响分析")
        social = rationality_data.社会稳定分析
        
        lines.append("\n## 合法性风险分析")
        lines.append(f"- 风险内容：{social.合法性风险.风险内容}")
        lines.append(f"- 风险等级：{social.合法性风险.风险等级}")
        lines.append(f"- 防范措施：")
        for i, measure in enumerate(social.合法性风险.防范措施, 1):
            lines.append(f"  {i}. {measure}")
        
        lines.append("\n## 生活环境风险分析")
        lines.append(f"- 风险内容：{social.生活环境风险.风险内容}")
        lines.append(f"- 风险等级：{social.生活环境风险.风险等级}")
        lines.append(f"- 防范措施：")
        for i, measure in enumerate(social.生活环境风险.防范措施, 1):
            lines.append(f"  {i}. {measure}")
        
        lines.append("\n## 社会环境风险分析")
        lines.append(f"- 风险内容：{social.社会环境风险.风险内容}")
        lines.append(f"- 风险等级：{social.社会环境风险.风险等级}")
        lines.append(f"- 防范措施：")
        for i, measure in enumerate(social.社会环境风险.防范措施, 1):
            lines.append(f"  {i}. {measure}")
        
        lines.append(f"- 社会稳定小结：{social.社会稳定小结}")
        
        # 添加节能分析
        lines.append("\n# 节能分析")
        energy = rationality_data.节能分析
        lines.append(f"- 前期工作节地措施：")
        for i, measure in enumerate(energy.前期工作节地措施, 1):
            lines.append(f"  {i}. {measure}")
        lines.append(f"- 建设实施节能措施：")
        for i, measure in enumerate(energy.建设实施节能措施, 1):
            lines.append(f"  {i}. {measure}")
        if energy.施工节能措施:
            lines.append(f"- 施工节能措施：")
            for i, measure in enumerate(energy.施工节能措施, 1):
                lines.append(f"  {i}. {measure}")
        if energy.运营节能措施:
            lines.append(f"- 运营节能措施：")
            for i, measure in enumerate(energy.运营节能措施, 1):
                lines.append(f"  {i}. {measure}")
        lines.append(f"- 节能结论：{energy.节能结论}")
        
        # 添加合理性结论
        lines.append("\n# 选址合理性分析小结")
        lines.append(rationality_data.合理性结论)
        
        # 添加图表清单
        if rationality_data.图表清单:
            lines.append("\n# 图表清单")
            for i, chart in enumerate(rationality_data.图表清单, 1):
                lines.append(f"{i}. {chart}")
        
        # 添加数据来源
        if rationality_data.数据来源:
            lines.append(f"\n# 数据来源")
            lines.append(rationality_data.数据来源)
        
        # 添加任务指令
        lines.append("\n" + "=" * 60)
        lines.append("请根据以上提供的数据，严格按照提示词模板的要求，")
        lines.append("生成第4章《建设项目选址合理性分析》的完整内容。")
        lines.append("确保覆盖全部6个子节，字数3000-5000字，使用专业规范的规划语言。")
        lines.append("=" * 60)
        
        user_message = "\n".join(lines)
        logger.info(f"用户消息构建完成 ({len(user_message)} 字符)")
        
        return user_message
    
    def get_agent(self) -> AssistantAgent:
        """
        获取AutoGen Agent实例
        
        Returns:
            AutoGen AssistantAgent实例
        """
        return self.agent
    
    def get_agent_info(self) -> Dict[str, Any]:
        """
        获取Agent信息
        
        Returns:
            Agent信息字典
        """
        return {
            "name": self.agent.name,
            "description": self.agent.description,
            "system_message_length": len(self.system_message),
            "template_path": self.template_path,
        }
    
    async def generate(
        self,
        rationality_data: RationalityData,
        context: str = None
    ) -> str:
        """
        生成第4章：选址合理性分析
        
        Args:
            rationality_data: 选址合理性分析数据（RationalityData模型）
            context: 可选的上下文信息（如第1-3章的摘要）
            
        Returns:
            生成的第4章内容（Markdown格式）
        """
        logger.info("开始生成第4章：选址合理性分析")
        logger.info(f"  项目名称：{rationality_data.项目基本信息.get('项目名称', '未知')}")
        
        try:
            # 1. 数据验证
            self._validate_data(rationality_data)
            
            # 2. 构建用户消息
            user_message = self._build_user_message(rationality_data, context)
            
            # 3. 调用Agent生成内容
            result = await self.agent.run(task=user_message)
            
            # 4. 提取响应内容
            if result and result.messages:
                last_message = result.messages[-1]
                if isinstance(last_message, TextMessage):
                    content = last_message.content
                else:
                    content = str(last_message.content)
                
                logger.info(f"第4章生成成功，字数: {len(content)}")
                return content
            else:
                raise ValueError("Agent没有返回任何内容")
        
        except Exception as e:
            logger.error(f"第4章生成失败: {str(e)}")
            raise
    
    async def generate_stream(
        self,
        rationality_data: RationalityData,
        context: str = None
    ):
        """
        流式生成第4章内容
        
        Args:
            rationality_data: 选址合理性分析数据
            context: 可选的上下文信息
            
        Yields:
            消息流
        """
        logger.info("开始流式生成第4章：选址合理性分析")
        
        self._validate_data(rationality_data)
        user_message = self._build_user_message(rationality_data, context)
        
        async for message in self.agent.run_stream(task=user_message):
            yield message


# 测试代码
if __name__ == "__main__":
    import asyncio
    
    async def test_agent():
        print("测试选址合理性分析Agent初始化...")
        
        try:
            from src.core.autogen_config import get_model_client
            from src.models.rationality_data import get_sample_data
            
            # 获取模型客户端
            model_client = get_model_client()
            
            # 初始化Agent
            agent = RationalityAnalysisAgent(model_client)
            
            # 获取Agent信息
            info = agent.get_agent_info()
            print("\n✓ Agent初始化成功!")
            print(f"  Agent名称: {info['name']}")
            print(f"  模板路径: {info['template_path']}")
            print(f"  System Message长度: {info['system_message_length']} 字符")
            
            # 测试用户消息构建
            print("\n测试用户消息构建...")
            test_data = get_sample_data()
            user_message = agent._build_user_message(test_data)
            print(f"✓ 用户消息构建成功 ({len(user_message)} 字符)")
            
            # 显示前800字符
            print("\n用户消息预览：")
            print(user_message[:800])
            
        except Exception as e:
            print(f"\n✗ Agent初始化失败: {str(e)}")
            import traceback
            traceback.print_exc()
    
    asyncio.run(test_agent())