"""
合法合规性分析Agent - 基于AutoGen (新版 autogen-agentchat API)

负责生成规划选址论证报告的第3章"建设项目合法合规性分析"。
"""

import os
from typing import Dict, Any, Optional
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient

from src.models.compliance_data import ComplianceData
from src.utils.logger import logger


class ComplianceAnalysisAgent:
    """
    合法合规性分析Agent
    
    使用AutoGen的AssistantAgent，专门负责生成第3章"合法合规性分析"内容。
    
    该Agent需要处理以下内容：
    - 法规政策符合性分析
    - 三线协调分析
    - 国土空间总体规划符合性
    - 专项规划符合性
    - 其他相关规划符合性
    - 过渡期内城乡总体规划符合性
    - 合法合规性小结
    """
    
    def __init__(
        self,
        model_client: OpenAIChatCompletionClient,
        prompt_template_path: str = None
    ):
        """
        初始化合法合规性分析Agent
        
        Args:
            model_client: OpenAIChatCompletionClient 实例
            prompt_template_path: 提示词模板路径，默认为templates/prompts/compliance_analysis.md
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
                "compliance_analysis.md"
            )
        
        # 加载system_message
        self.system_message = self._load_system_message(prompt_template_path)
        self.template_path = prompt_template_path
        
        # 创建AutoGen AssistantAgent
        self.agent = AssistantAgent(
            name="compliance_analysis_agent",
            model_client=self.model_client,
            system_message=self.system_message,
            description="负责生成规划选址论证报告第3章'建设项目合法合规性分析'的专业AI Agent"
        )
        
        logger.info(f"合法合规性分析Agent初始化完成")
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
    
    def _validate_data(self, data: ComplianceData):
        """
        验证输入数据
        
        Args:
            data: 合法合规性分析数据
            
        Raises:
            ValueError: 数据验证失败
        """
        # Pydantic已经做了基本验证，这里做业务逻辑验证
        if not data.项目基本信息:
            raise ValueError("项目基本信息不能为空")
        
        if not data.合法合规小结:
            raise ValueError("合法合规小结不能为空")
        
        logger.info("数据验证通过")
    
    def _build_user_message(
        self,
        compliance_data: ComplianceData,
        context: str = None
    ) -> str:
        """
        构建发送给Agent的用户消息
        
        Args:
            compliance_data: 合法合规性分析数据
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
        for key, value in compliance_data.项目基本信息.items():
            lines.append(f"- {key}：{value}")
        
        # 添加法规政策符合性分析
        lines.append("\n# 法规政策符合性分析")
        
        ## 产业政策符合性
        lines.append("\n## 产业政策符合性")
        industry_policy = compliance_data.产业政策符合性
        lines.append(f"- 法规名称：{industry_policy.法规名称}")
        if industry_policy.发布单位:
            lines.append(f"- 发布单位：{industry_policy.发布单位}")
        if industry_policy.发布时间:
            lines.append(f"- 发布时间：{industry_policy.发布时间}")
        lines.append(f"- 符合性分析：{industry_policy.符合性分析}")
        lines.append(f"- 符合性结论：{industry_policy.符合性结论}")
        
        ## 供地政策符合性
        lines.append("\n## 供地政策符合性")
        land_policy = compliance_data.供地政策符合性
        lines.append(f"- 法规名称：{land_policy.法规名称}")
        if land_policy.发布单位:
            lines.append(f"- 发布单位：{land_policy.发布单位}")
        if land_policy.发布时间:
            lines.append(f"- 发布时间：{land_policy.发布时间}")
        lines.append(f"- 符合性分析：{land_policy.符合性分析}")
        lines.append(f"- 符合性结论：{land_policy.符合性结论}")
        
        ## 其他法规符合性
        if compliance_data.其他法规符合性:
            lines.append("\n## 其他法规符合性")
            for i, reg in enumerate(compliance_data.其他法规符合性, 1):
                lines.append(f"\n### 法规{i}：{reg.法规名称}")
                if reg.发布单位:
                    lines.append(f"- 发布单位：{reg.发布单位}")
                if reg.发布时间:
                    lines.append(f"- 发布时间：{reg.发布时间}")
                lines.append(f"- 符合性分析：{reg.符合性分析}")
                lines.append(f"- 符合性结论：{reg.符合性结论}")
        
        # 添加三线协调分析
        lines.append("\n# 三线协调分析")
        three_lines = compliance_data.三线协调分析
        lines.append(f"- 是否占用耕地：{'是' if three_lines.是否占用耕地 else '否'}")
        if three_lines.耕地面积:
            lines.append(f"  - 占用耕地面积：{three_lines.耕地面积}")
        lines.append(f"- 是否占用永久基本农田：{'是' if three_lines.是否占用永久基本农田 else '否'}")
        if three_lines.永久基本农田面积:
            lines.append(f"  - 占用永久基本农田面积：{three_lines.永久基本农田面积}")
        lines.append(f"- 是否占用生态保护红线：{'是' if three_lines.是否占用生态保护红线 else '否'}")
        if three_lines.生态保护红线面积:
            lines.append(f"  - 占用生态保护红线面积：{three_lines.生态保护红线面积}")
        lines.append(f"- 是否位于城镇开发边界内：{'是' if three_lines.是否占用城镇开发边界 else '否'}")
        if three_lines.城镇开发边界说明:
            lines.append(f"  - 城镇开发边界说明：{three_lines.城镇开发边界说明}")
        lines.append(f"- 符合性说明：{three_lines.符合性说明}")
        if three_lines.数据来源:
            lines.append(f"- 数据来源：{three_lines.数据来源}")
        
        # 添加国土空间总体规划符合性
        lines.append("\n# 国土空间总体规划符合性")
        spatial = compliance_data.国土空间规划符合性
        
        ## 一张图分析
        lines.append('\n## "一张图"上图落位情况')
        one_map = spatial.一张图分析
        lines.append(f"- 是否上图落位：{'是' if one_map.是否上图 else '否'}")
        if one_map.重点项目库名称:
            lines.append(f"- 重点项目库名称：{one_map.重点项目库名称}")
        if one_map.项目类型:
            lines.append(f"- 项目类型：{one_map.项目类型}")
        lines.append(f"- 落位说明：{one_map.落位说明}")
        
        ## 功能分区准入
        lines.append("\n## 功能分区准入分析")
        func_zone = spatial.功能分区准入
        lines.append(f"- 城镇建设适宜性：{func_zone.城镇建设适宜性}")
        lines.append(f"- 生态保护重要性：{func_zone.生态保护重要性}")
        lines.append(f"- 农业生产适宜性：{func_zone.农业生产适宜性}")
        lines.append(f"- 符合性说明：{func_zone.符合性说明}")
        
        ## 用途管制和总体格局
        lines.append("\n## 用途管制符合性")
        lines.append(spatial.用途管制符合性)
        
        lines.append("\n## 国土空间总体格局符合性")
        lines.append(spatial.国土空间格局符合性)
        
        lines.append("\n## 总体符合性结论")
        lines.append(spatial.总体符合性结论)
        
        # 添加专项规划符合性
        lines.append("\n# 专项规划符合性")
        special = compliance_data.专项规划符合性
        
        lines.append("\n## 综合交通体系规划")
        lines.append(f"- 规划名称：{special.综合交通规划.规划名称}")
        lines.append(f"- 符合性分析：{special.综合交通规划.符合性分析}")
        lines.append(f"- 符合性结论：{special.综合交通规划.符合性结论}")
        
        lines.append("\n## 市政基础设施规划")
        lines.append(f"- 规划名称：{special.市政基础设施规划.规划名称}")
        lines.append(f"- 符合性分析：{special.市政基础设施规划.符合性分析}")
        lines.append(f"- 符合性结论：{special.市政基础设施规划.符合性结论}")
        
        lines.append("\n## 历史文化遗产保护规划")
        lines.append(f"- 规划名称：{special.历史文化遗产保护规划.规划名称}")
        lines.append(f"- 符合性分析：{special.历史文化遗产保护规划.符合性分析}")
        lines.append(f"- 符合性结论：{special.历史文化遗产保护规划.符合性结论}")
        
        lines.append("\n## 综合防灾工程规划")
        lines.append(f"- 规划名称：{special.综合防灾工程规划.规划名称}")
        lines.append(f"- 符合性分析：{special.综合防灾工程规划.符合性分析}")
        lines.append(f"- 符合性结论：{special.综合防灾工程规划.符合性结论}")
        
        lines.append("\n## 旅游规划")
        lines.append(f"- 规划名称：{special.旅游规划.规划名称}")
        lines.append(f"- 符合性分析：{special.旅游规划.符合性分析}")
        lines.append(f"- 符合性结论：{special.旅游规划.符合性结论}")
        
        if special.环境保护规划:
            lines.append("\n## 环境保护规划")
            lines.append(f"- 规划名称：{special.环境保护规划.规划名称}")
            lines.append(f"- 符合性分析：{special.环境保护规划.符合性分析}")
            lines.append(f"- 符合性结论：{special.环境保护规划.符合性结论}")
        
        if special.自然保护地规划:
            lines.append("\n## 自然保护地规划")
            lines.append(f"- 规划名称：{special.自然保护地规划.规划名称}")
            lines.append(f"- 符合性分析：{special.自然保护地规划.符合性分析}")
            lines.append(f"- 符合性结论：{special.自然保护地规划.符合性结论}")
        
        # 添加其他相关规划符合性
        lines.append("\n# 其他相关规划符合性")
        other = compliance_data.其他规划符合性
        
        lines.append("\n## 国民经济和社会发展规划")
        lines.append(f"- 规划名称：{other.国民经济和社会发展规划.规划名称}")
        lines.append(f"- 符合性分析：{other.国民经济和社会发展规划.符合性分析}")
        lines.append(f"- 符合性结论：{other.国民经济和社会发展规划.符合性结论}")
        
        lines.append("\n## 生态环境保护规划")
        lines.append(f"- 规划名称：{other.生态环境保护规划.规划名称}")
        lines.append(f"- 符合性分析：{other.生态环境保护规划.符合性分析}")
        lines.append(f"- 符合性结论：{other.生态环境保护规划.符合性结论}")
        
        lines.append('\n## "三线一单"生态环境分区管控')
        lines.append(f'- 规划名称：{other.三线一单生态环境分区管控.规划名称}')
        lines.append(f'- 符合性分析：{other.三线一单生态环境分区管控.符合性分析}')
        lines.append(f'- 符合性结论：{other.三线一单生态环境分区管控.符合性结论}')
        
        if other.综合交通体系规划:
            lines.append("\n## 综合交通体系规划")
            lines.append(f"- 规划名称：{other.综合交通体系规划.规划名称}")
            lines.append(f"- 符合性分析：{other.综合交通体系规划.符合性分析}")
            lines.append(f"- 符合性结论：{other.综合交通体系规划.符合性结论}")
        
        # 添加过渡期内城乡总体规划符合性
        if compliance_data.城乡总体规划符合性:
            lines.append("\n# 过渡期内城乡总体规划符合性")
            urban = compliance_data.城乡总体规划符合性
            lines.append(f"- 规划名称：{urban.规划名称}")
            lines.append(f"- 规划期限：{urban.规划期限}")
            lines.append(f"- 空间管制分区：{urban.空间管制分区}")
            lines.append(f"- 符合性分析：{urban.符合性分析}")
            lines.append(f"- 符合性结论：{urban.符合性结论}")
        
        # 添加合法合规小结
        lines.append("\n# 合法合规性小结")
        lines.append(compliance_data.合法合规小结)
        
        # 添加图表清单
        if compliance_data.图表清单:
            lines.append("\n# 图表清单")
            for i, chart in enumerate(compliance_data.图表清单, 1):
                lines.append(f"{i}. {chart}")
        
        # 添加数据来源
        if compliance_data.数据来源:
            lines.append(f"\n# 数据来源")
            lines.append(compliance_data.数据来源)
        
        # 添加任务指令
        lines.append("\n" + "=" * 60)
        lines.append("请根据以上提供的数据，严格按照提示词模板的要求，")
        lines.append("生成第3章《建设项目合法合规性分析》的完整内容。")
        lines.append("确保覆盖全部7个子节，字数4000-6000字，使用专业规范的规划语言。")
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
        compliance_data: ComplianceData,
        context: str = None
    ) -> str:
        """
        生成第3章：合法合规性分析

        Args:
            compliance_data: 合法合规性分析数据（ComplianceData模型）
            context: 可选的上下文信息（如第1、2章的摘要）

        Returns:
            生成的第3章内容（Markdown格式）
        """
        logger.info("开始生成第3章：合法合规性分析")
        logger.info(f"  项目名称：{compliance_data.项目基本信息.get('项目名称', '未知')}")
        
        try:
            # 1. 数据验证
            self._validate_data(compliance_data)
            
            # 2. 构建用户消息
            user_message = self._build_user_message(compliance_data, context)
            
            # 3. 调用Agent生成内容
            result = await self.agent.run(task=user_message)
            
            # 4. 提取响应内容
            if result and result.messages:
                last_message = result.messages[-1]
                if isinstance(last_message, TextMessage):
                    content = last_message.content
                else:
                    content = str(last_message.content)
                
                logger.info(f"第3章生成成功，字数: {len(content)}")
                return content
            else:
                raise ValueError("Agent没有返回任何内容")
        
        except Exception as e:
            logger.error(f"第3章生成失败: {str(e)}")
            raise

    async def generate_stream(
        self,
        compliance_data: ComplianceData,
        context: str = None
    ):
        """
        流式生成第3章内容

        Args:
            compliance_data: 合法合规性分析数据
            context: 可选的上下文信息

        Yields:
            消息流
        """
        logger.info("开始流式生成第3章：合法合规性分析")
        
        self._validate_data(compliance_data)
        user_message = self._build_user_message(compliance_data, context)
        
        async for message in self.agent.run_stream(task=user_message):
            yield message


# 测试代码
if __name__ == "__main__":
    import asyncio
    
    async def test_agent():
        print("测试合法合规性分析Agent初始化...")
        
        try:
            from src.core.autogen_config import get_model_client
            from src.models.compliance_data import get_sample_data
            
            # 获取模型客户端
            model_client = get_model_client()
            
            # 初始化Agent
            agent = ComplianceAnalysisAgent(model_client)
            
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