"""
扩展ExcelParser - 添加第3章数据解析方法

在ExcelParser中添加以下方法：
1. parse_compliance() - 解析合法合规性分析数据
2. _parse_regulation() - 解析法规政策Sheet
3. _parse_three_lines() - 解析三线分析Sheet
4. _parse_spatial_planning() - 解析国土空间规划Sheet
5. _parse_special_planning() - 解析专项规划Sheet
6. _parse_other_planning() - 解析其他规划Sheet
7. _parse_urban_planning() - 解析城乡总体规划Sheet
"""

import os
import sys

# 添加项目根目录到Python路径
# __file__ = /Users/yc/Applications/python/xuanzhi/scripts/add_chapter3_parser.py
# 向上两级: xuanzhi/scripts -> xuanzhi
# 向上三级: xuanzhi/scripts -> xuanzhi -> xuanzhi
# 所以需要 dirname 3次
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)  # xuanzhi
sys.path.insert(0, project_root)
print(f"项目根目录: {project_root}")


def add_chapter3_parser():
    """扩展ExcelParser添加第3章解析方法"""
    
    parser_file = os.path.join(project_root, "src", "services", "excel_parser.py")
    backup_file = os.path.join(project_root, "src", "services", "excel_parser_backup.py")
    
    print("=" * 80)
    print("扩展ExcelParser - 添加第3章数据解析方法")
    print("=" * 80)
    print(f"文件: {parser_file}")
    print()
    
    # 读取原始文件
    with open(parser_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 备份原始文件
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ 已备份原始文件到: {backup_file}")
    
    # 检查是否已存在ComplianceData导入
    if "from src.models.compliance_data import" not in content:
        # 添加导入
        import_section_end = content.find("# 测试代码")
        if import_section_end > 0:
            # 找到导入部分结束位置
            insert_pos = content.find("\nfrom src.models.site_selection_data import", import_section_end)
            if insert_pos > 0:
                # 在site_selection_data导入后添加compliance_data导入
                line_end = content.find("\n", insert_pos + 1)
                new_imports = "\nfrom src.models.compliance_data import ComplianceData"
                content = content[:line_end] + new_imports + content[line_end:]
                print("✓ 已添加ComplianceData导入")
    
    # 添加Sheet名称常量
    if "SHEET_REGULATION = \"法规政策\"" not in content:
        # 在SHEET_COMPARISON后添加新的Sheet常量
        old_constant = 'SHEET_COMPARISON = "方案比选"'
        new_constants = '''SHEET_COMPARISON = "方案比选"
    SHEET_REGULATION = "法规政策"
    SHEET_THREE_LINES = "三线分析"
    SHEET_SPATIAL_PLANNING = "国土空间规划"
    SHEET_SPECIAL_PLANNING = "专项规划"
    SHEET_OTHER_PLANNING = "其他规划"
    SHEET_URBAN_PLANNING = "城乡总体规划"
    SHEET_COMPLIANCE_SUMMARY = "合法合规小结"'''
        content = content.replace(old_constant, new_constants)
        print("✓ 已添加Sheet名称常量")
    
    # 添加parse_compliance方法（在parse_all方法之前）
    parse_compliance_method = '''
    def parse_compliance(self) -> ComplianceData:
        """
        解析合法合规性分析数据
        
        Returns:
            ComplianceData: 合法合规性分析数据模型
        """
        logger.info("开始解析合法合规性分析数据...")
        
        project_basic = self.parse_project_overview().to_dict()
        
        # 解析各Sheet
        regulation = self._parse_regulation()
        three_lines = self._parse_three_lines()
        spatial_planning = self._parse_spatial_planning()
        special_planning = self._parse_special_planning()
        other_planning = self._parse_other_planning()
        urban_planning = self._parse_urban_planning()
        summary = self._parse_compliance_summary()
        
        logger.info("合法合规性分析数据解析完成")
        
        return ComplianceData(
            项目基本信息=project_basic,
            产业政策符合性=regulation[0] if len(regulation) > 0 else None,
            供地政策符合性=regulation[1] if len(regulation) > 1 else None,
            其他法规符合性=regulation[2:] if len(regulation) > 2 else None,
            三线协调分析=three_lines,
            国土空间规划符合性=spatial_planning,
            专项规划符合性=special_planning,
            其他规划符合性=other_planning,
            城乡总体规划符合性=urban_planning,
            合法合规小结=summary,
            编制日期="2026年2月26日"
        )
    
    def _parse_regulation(self) -> list:
        """解析法规政策Sheet"""
        logger.info("  解析法规政策...")
        sheet = self._get_sheet(self.SHEET_REGULATION)
        
        if sheet is None:
            logger.warning(f"  Sheet不存在: {self.SHEET_REGULATION}")
            return []
        
        from src.models.compliance_data import RegulationCompliance
        regulations = []
        
        for row in sheet.iter_rows(min_row=2, values_only=True):
            if row[0] is None:
                continue
            
            try:
                reg = RegulationCompliance(
                    法规名称=str(row[0]) if row[0] else "",
                    发布单位=str(row[1]) if len(row) > 1 and row[1] else None,
                    发布时间=str(row[2]) if len(row) > 2 and row[2] else None,
                    符合性分析=str(row[3]) if len(row) > 3 and row[3] else "",
                    符合性结论=str(row[4]) if len(row) > 4 and row[4] else ""
                )
                regulations.append(reg)
            except Exception as e:
                logger.warning(f"  解析法规政策行失败: {str(e)}")
                continue
        
        logger.info(f"  解析到 {len(regulations)} 条法规政策")
        return regulations
    
    def _parse_three_lines(self):
        """解析三线分析Sheet"""
        logger.info("  解析三线分析...")
        sheet = self._get_sheet(self.SHEET_THREE_LINES)
        
        if sheet is None:
            logger.warning(f"  Sheet不存在: {self.SHEET_THREE_LINES}")
            from src.models.compliance_data import ThreeLinesAnalysis
            return ThreeLinesAnalysis(
                是否占用耕地=False,
                是否占用永久基本农田=False,
                是否占用生态保护红线=False,
                是否占用城镇开发边界=False,
                符合性说明="待补充"
            )
        
        data = self._read_key_value_sheet(sheet)
        from src.models.compliance_data import ThreeLinesAnalysis
        
        return ThreeLinesAnalysis(
            是否占用耕地=self._parse_bool(data.get("是否占用耕地", "否")),
            耕地面积=data.get("占用耕地面积（平方米）"),
            是否占用永久基本农田=self._parse_bool(data.get("是否占用永久基本农田", "否")),
            永久基本农田面积=data.get("占用永久基本农田面积（平方米）"),
            是否占用生态保护红线=self._parse_bool(data.get("是否占用生态保护红线", "否")),
            生态保护红线面积=data.get("占用生态保护红线面积（平方米）"),
            是否占用城镇开发边界=self._parse_bool(data.get("是否位于城镇开发边界内", "否")),
            城镇开发边界说明=data.get("城镇开发边界说明"),
            符合性说明=data.get("符合性说明", ""),
            数据来源=data.get("数据来源")
        )
    
    def _parse_spatial_planning(self):
        """解析国土空间规划Sheet"""
        logger.info("  解析国土空间规划...")
        sheet = self._get_sheet(self.SHEET_SPATIAL_PLANNING)
        
        if sheet is None:
            logger.warning(f"  Sheet不存在: {self.SHEET_SPATIAL_PLANNING}")
            from src.models.compliance_data import SpatialPlanningCompliance, OneMapAnalysis, FunctionalZoneAnalysis
            return SpatialPlanningCompliance(
                一张图分析=OneMapAnalysis(是否上图=False, 落位说明=""),
                功能分区准入=FunctionalZoneAnalysis(城镇建设适宜性="", 生态保护重要性="", 农业生产适宜性="", 符合性说明=""),
                用途管制符合性="",
                国土空间格局符合性="",
                总体符合性结论=""
            )
        
        # 读取分类格式
        category_data = self._read_category_sheet(sheet)
        
        from src.models.compliance_data import (
            SpatialPlanningCompliance, OneMapAnalysis, FunctionalZoneAnalysis
        )
        
        # 一张图分析
        one_map_data = category_data.get("一张图落位", {})
        one_map = OneMapAnalysis(
            是否上图=one_map_data.get("是否上图落位", "是") == "是",
            重点项目库名称=one_map_data.get("重点项目库名称"),
            项目类型=one_map_data.get("项目类型"),
            落位说明=one_map_data.get("落位说明", "")
        )
        
        # 功能分区准入
        func_zone_data = category_data.get("功能分区准入", {})
        func_zone = FunctionalZoneAnalysis(
            城镇建设适宜性=func_zone_data.get("城镇建设适宜性", ""),
            生态保护重要性=func_zone_data.get("生态保护重要性", ""),
            农业生产适宜性=func_zone_data.get("农业生产适宜性", ""),
            符合性说明=func_zone_data.get("符合性说明", "")
        )
        
        # 用途管制和总体格局
        usage_data = category_data.get("用途管制", {})
        spatial_data = category_data.get("总体格局", {})
        conclusion_data = category_data.get("总体结论", {})
        
        return SpatialPlanningCompliance(
            一张图分析=one_map,
            功能分区准入=func_zone,
            用途管制符合性=usage_data.get("符合性说明", ""),
            国土空间格局符合性=spatial_data.get("符合性说明", ""),
            总体符合性结论=conclusion_data.get("总体符合性结论", "")
        )
    
    def _parse_special_planning(self):
        """解析专项规划Sheet"""
        logger.info("  解析专项规划...")
        sheet = self._get_sheet(self.SHEET_SPECIAL_PLANNING)
        
        if sheet is None:
            logger.warning(f"  Sheet不存在: {self.SHEET_SPECIAL_PLANNING}")
            from src.models.compliance_data import SpecialPlanningCompliance, SpecialPlanCompliance
            return SpecialPlanningCompliance(
                综合交通规划=SpecialPlanCompliance(规划名称="", 符合性分析="", 符合性结论=""),
                市政基础设施规划=SpecialPlanCompliance(规划名称="", 符合性分析="", 符合性结论=""),
                历史文化遗产保护规划=SpecialPlanCompliance(规划名称="", 符合性分析="", 符合性结论=""),
                综合防灾工程规划=SpecialPlanCompliance(规划名称="", 符合性分析="", 符合性结论=""),
                旅游规划=SpecialPlanCompliance(规划名称="", 符合性分析="", 符合性结论="")
            )
        
        from src.models.compliance_data import SpecialPlanningCompliance, SpecialPlanCompliance
        
        special_plans = {
            "综合交通规划": None,
            "市政基础设施规划": None,
            "历史文化遗产保护规划": None,
            "综合防灾工程规划": None,
            "旅游规划": None,
            "环境保护规划": None,
            "自然保护地规划": None,
        }
        
        for row in sheet.iter_rows(min_row=2, values_only=True):
            if row[0] is None:
                continue
            
            plan_type = str(row[0]).strip()
            plan_name = str(row[1]) if len(row) > 1 and row[1] else ""
            analysis = str(row[2]) if len(row) > 2 and row[2] else ""
            conclusion = str(row[3]) if len(row) > 3 and row[3] else ""
            
            plan = SpecialPlanCompliance(
                规划名称=plan_name,
                符合性分析=analysis,
                符合性结论=conclusion
            )
            
            if plan_type in special_plans:
                special_plans[plan_type] = plan
        
        return SpecialPlanningCompliance(
            综合交通规划=special_plans.get("综合交通规划") or SpecialPlanCompliance(规划名称="", 符合性分析="", 符合性结论=""),
            市政基础设施规划=special_plans.get("市政基础设施规划") or SpecialPlanCompliance(规划名称="", 符合性分析="", 符合性结论=""),
            历史文化遗产保护规划=special_plans.get("历史文化遗产保护规划") or SpecialPlanCompliance(规划名称="", 符合性分析="", 符合性结论=""),
            综合防灾工程规划=special_plans.get("综合防灾工程规划") or SpecialPlanCompliance(规划名称="", 符合性分析="", 符合性结论=""),
            旅游规划=special_plans.get("旅游规划") or SpecialPlanCompliance(规划名称="", 符合性分析="", 符合性结论=""),
            环境保护规划=special_plans.get("环境保护规划"),
            自然保护地规划=special_plans.get("自然保护地规划")
        )
    
    def _parse_other_planning(self):
        """解析其他规划Sheet"""
        logger.info("  解析其他规划...")
        sheet = self._get_sheet(self.SHEET_OTHER_PLANNING)
        
        if sheet is None:
            logger.warning(f"  Sheet不存在: {self.SHEET_OTHER_PLANNING}")
            from src.models.compliance_data import OtherPlanningCompliance, SpecialPlanCompliance
            return OtherPlanningCompliance(
                国民经济和社会发展规划=SpecialPlanCompliance(规划名称="", 符合性分析="", 符合性结论=""),
                生态环境保护规划=SpecialPlanCompliance(规划名称="", 符合性分析="", 符合性结论=""),
                三线一单生态环境分区管控=SpecialPlanCompliance(规划名称="", 符合性分析="", 符合性结论="")
            )
        
        from src.models.compliance_data import OtherPlanningCompliance, SpecialPlanCompliance
        
        other_plans = {}
        
        for row in sheet.iter_rows(min_row=2, values_only=True):
            if row[0] is None:
                continue
            
            plan_type = str(row[0]).strip()
            plan_name = str(row[1]) if len(row) > 1 and row[1] else ""
            analysis = str(row[2]) if len(row) > 2 and row[2] else ""
            conclusion = str(row[3]) if len(row) > 3 and row[3] else ""
            
            plan = SpecialPlanCompliance(
                规划名称=plan_name,
                符合性分析=analysis,
                符合性结论=conclusion
            )
            
            other_plans[plan_type] = plan
        
        return OtherPlanningCompliance(
            国民经济和社会发展规划=other_plans.get("国民经济和社会发展规划") or SpecialPlanCompliance(规划名称="", 符合性分析="", 符合性结论=""),
            生态环境保护规划=other_plans.get("生态环境保护规划") or SpecialPlanCompliance(规划名称="", 符合性分析="", 符合性结论=""),
            三线一单生态环境分区管控=other_plans.get("三线一单生态环境分区管控") or SpecialPlanCompliance(规划名称="", 符合性分析="", 符合性结论=""),
            综合交通体系规划=other_plans.get("综合交通体系规划")
        )
    
    def _parse_urban_planning(self):
        """解析城乡总体规划Sheet"""
        logger.info("  解析城乡总体规划...")
        sheet = self._get_sheet(self.SHEET_URBAN_PLANNING)
        
        if sheet is None:
            logger.warning(f"  Sheet不存在: {self.SHEET_URBAN_PLANNING}")
            return None
        
        data = self._read_key_value_sheet(sheet)
        from src.models.compliance_data import UrbanPlanningCompliance
        
        return UrbanPlanningCompliance(
            规划名称=data.get("规划名称", ""),
            规划期限=data.get("规划期限", ""),
            空间管制分区=data.get("空间管制分区", ""),
            符合性分析=data.get("符合性分析", ""),
            符合性结论=data.get("符合性结论", "")
        )
    
    def _parse_compliance_summary(self) -> str:
        """解析合法合规小结"""
        logger.info("  解析合法合规小结...")
        sheet = self._get_sheet(self.SHEET_COMPLIANCE_SUMMARY)
        
        if sheet is None:
            logger.warning(f"  Sheet不存在: {self.SHEET_COMPLIANCE_SUMMARY}")
            return "待补充"
        
        data = self._read_key_value_sheet(sheet)
        return data.get("合法合规小结", "")

'''
    
    # 查找parse_all方法的位置
    parse_all_pos = content.find("def parse_all(self)")
    
    if parse_all_pos > 0:
        # 在parse_all方法之前插入新方法
        content = content[:parse_all_pos] + parse_compliance_method + "\n" + content[parse_all_pos:]
        print("✓ 已添加parse_compliance方法")
    else:
        print("✗ 未找到parse_all方法位置")
        return False
    
    # 修改parse_all方法以包含compliance数据
    old_parse_all = '''def parse_all(self) -> Tuple[ProjectOverviewData, SiteSelectionData]:
        """
        解析所有数据
        
        Returns:
            (ProjectOverviewData, SiteSelectionData) 元组
        """
        logger.info(f"开始解析Excel文件: {self.file_path}")
        
        project_overview = self.parse_project_overview()
        site_selection = self.parse_site_selection()
        
        logger.info("Excel文件解析完成")
        return project_overview, site_selection'''
    
    new_parse_all = '''def parse_all(self) -> Tuple[ProjectOverviewData, SiteSelectionData, ComplianceData]:
        """
        解析所有数据
        
        Returns:
            (ProjectOverviewData, SiteSelectionData, ComplianceData) 元组
        """
        logger.info(f"开始解析Excel文件: {self.file_path}")
        
        project_overview = self.parse_project_overview()
        site_selection = self.parse_site_selection()
        compliance = self.parse_compliance()
        
        logger.info("Excel文件解析完成")
        return project_overview, site_selection, compliance'''
    
    content = content.replace(old_parse_all, new_parse_all)
    print("✓ 已更新parse_all方法返回三元组")
    
    # 保存修改后的文件
    with open(parser_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ 已保存更新到: {parser_file}")
    print()
    print("=" * 80)
    print("ExcelParser扩展完成！")
    print("=" * 80)
    print()
    print("新增方法:")
    print("  - parse_compliance() - 解析合法合规性分析数据")
    print("  - _parse_regulation() - 解析法规政策Sheet")
    print("  - _parse_three_lines() - 解析三线分析Sheet")
    print("  - _parse_spatial_planning() - 解析国土空间规划Sheet")
    print("  - _parse_special_planning() - 解析专项规划Sheet")
    print("  - _parse_other_planning() - 解析其他规划Sheet")
    print("  - _parse_urban_planning() - 解析城乡总体规划Sheet")
    print("  - _parse_compliance_summary() - 解析合法合规小结")
    print()
    print("下一步：进行端到端测试")
    
    return True


if __name__ == "__main__":
    success = add_chapter3_parser()
    sys.exit(0 if success else 1)