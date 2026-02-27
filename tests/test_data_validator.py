"""
数据验证工作流集成测试

测试完整的验证流程:
1. 验证原始数据
2. 填充缺失字段
3. 再次验证确认完整
"""

import pytest
import shutil
from pathlib import Path
from src.services.excel_parser import ExcelParser
from src.services.data_validator import DataValidator, validate_excel_file


class TestDataValidator:
    """数据验证器测试"""
    
    @pytest.fixture
    def template_path(self) -> Path:
        """获取模板文件路径"""
        return Path("templates/excel_templates/项目数据模板.xlsx")
    
    @pytest.fixture
    def test_output_dir(self) -> Path:
        """创建测试输出目录"""
        output_dir = Path("output/test_validation")
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir
    
    def test_validator_initialization(self):
        """测试验证器初始化"""
        validator = DataValidator()
        assert validator.REQUIRED_FIELDS is not None
        assert len(validator.REQUIRED_FIELDS) > 0
        assert "项目基本信息" in validator.REQUIRED_FIELDS
    
    def test_validate_excel_file(self, template_path):
        """测试便捷验证函数"""
        if not template_path.exists():
            pytest.skip(f"模板文件不存在: {template_path}")
        
        report = validate_excel_file(str(template_path))
        
        assert report is not None
        assert report.file_name == str(template_path)
        assert report.total_sheets > 0
        assert report.completion_rate >= 0
    
    def test_validate_sheet(self, template_path):
        """测试单个Sheet验证"""
        if not template_path.exists():
            pytest.skip(f"模板文件不存在: {template_path}")
        
        parser = ExcelParser(str(template_path))
        validator = DataValidator()
        
        # 验证项目基本信息
        result = validator.validate_sheet(parser, "项目基本信息")
        
        assert result.sheet_name == "项目基本信息"
        assert result.total_fields == 6
        assert result.valid_fields >= 0
        assert result.missing_fields >= 0
        
        parser.close()
    
    def test_validate_all_sheets(self, template_path):
        """测试所有Sheet验证"""
        if not template_path.exists():
            pytest.skip(f"模板文件不存在: {template_path}")
        
        parser = ExcelParser(str(template_path))
        validator = DataValidator()
        
        report = validator.validate_all(parser)
        
        assert report is not None
        assert report.total_sheets > 0
        assert len(report.sheet_results) == report.total_sheets
        
        # 检查JSON输出
        json_output = report.to_json()
        assert "file_name" in json_output
        assert "summary" in json_output
        
        # 检查Markdown输出
        md_output = report.to_markdown()
        assert "# 数据验证报告" in md_output
        
        parser.close()
    
    def test_get_missing_fields(self, template_path):
        """测试获取缺失字段"""
        if not template_path.exists():
            pytest.skip(f"模板文件不存在: {template_path}")
        
        parser = ExcelParser(str(template_path))
        missing = parser.get_missing_fields()
        
        assert isinstance(missing, dict)
        # 应该有一些缺失字段
        assert len(missing) > 0
        
        parser.close()
    
    def test_fill_missing_fields(self, template_path, test_output_dir):
        """测试填充缺失字段"""
        if not template_path.exists():
            pytest.skip(f"模板文件不存在: {template_path}")
        
        # 复制文件用于测试
        test_file = test_output_dir / "test_fill.xlsx"
        shutil.copy(template_path, test_file)
        
        # 验证原始数据
        parser = ExcelParser(str(test_file))
        report_before = parser.validate_data()
        initial_missing = report_before.missing_fields
        
        # 填充缺失字段
        stats = parser.fill_missing_data()
        
        # 重新验证
        parser2 = ExcelParser(str(test_file))
        report_after = parser2.validate_data()
        
        # 验证填充效果
        # 注意：fill_missing_data 只填充键值对格式的Sheet
        total_filled = sum(stats.values())
        assert total_filled > 0, "应该填充了至少一个字段"
        
        parser.close()
        parser2.close()
    
    def test_validation_report_properties(self):
        """测试验证报告属性"""
        from src.services.data_validator import (
            FieldValidationResult,
            SheetValidationResult,
            ValidationReport
        )
        from datetime import datetime
        
        # 创建测试数据
        field_result = FieldValidationResult(
            field_name="测试字段",
            status="valid",
            value="测试值"
        )
        
        sheet_result = SheetValidationResult(
            sheet_name="测试Sheet",
            total_fields=5,
            valid_fields=3,
            missing_fields=2,
            field_results=[field_result]
        )
        
        report = ValidationReport(
            file_name="test.xlsx",
            validation_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            total_sheets=1,
            total_fields=5,
            valid_fields=3,
            missing_fields=2,
            sheet_results=[sheet_result]
        )
        
        # 测试属性
        assert report.is_complete == False
        assert report.completion_rate == 60.0
        assert sheet_result.is_complete == False
        assert sheet_result.completion_rate == 60.0
    
    def test_parser_validate_data_method(self, template_path):
        """测试Parser的validate_data方法"""
        if not template_path.exists():
            pytest.skip(f"模板文件不存在: {template_path}")
        
        parser = ExcelParser(str(template_path))
        
        # 测试validate_data方法
        report = parser.validate_data()
        
        assert report is not None
        assert report.file_name == str(template_path)
        
        parser.close()
    
    def test_parser_get_missing_fields_method(self, template_path):
        """测试Parser的get_missing_fields方法"""
        if not template_path.exists():
            pytest.skip(f"模板文件不存在: {template_path}")
        
        parser = ExcelParser(str(template_path))
        
        # 测试get_missing_fields方法
        missing = parser.get_missing_fields()
        
        assert isinstance(missing, dict)
        
        parser.close()


class TestValidationWorkflow:
    """完整验证工作流测试"""
    
    @pytest.fixture
    def template_path(self) -> Path:
        return Path("templates/excel_templates/项目数据模板.xlsx")
    
    @pytest.fixture
    def test_output_dir(self) -> Path:
        output_dir = Path("output/test_validation")
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir
    
    def test_full_workflow(self, template_path, test_output_dir):
        """
        测试完整工作流:
        1. 验证原始数据
        2. 获取缺失字段
        3. 填充缺失字段
        4. 再次验证
        """
        if not template_path.exists():
            pytest.skip(f"模板文件不存在: {template_path}")
        
        # 步骤1: 复制文件
        test_file = test_output_dir / "workflow_test.xlsx"
        shutil.copy(template_path, test_file)
        
        # 步骤2: 验证原始数据
        parser = ExcelParser(str(test_file))
        report1 = parser.validate_data()
        
        print(f"\n原始数据完整率: {report1.completion_rate:.1f}%")
        print(f"缺失字段数: {report1.missing_fields}")
        
        # 步骤3: 获取缺失字段
        missing = parser.get_missing_fields()
        print(f"缺失字段Sheet数: {len(missing)}")
        
        # 步骤4: 填充缺失字段
        stats = parser.fill_missing_data()
        total_filled = sum(stats.values())
        print(f"填充字段数: {total_filled}")
        
        # 步骤5: 再次验证
        parser2 = ExcelParser(str(test_file))
        report2 = parser2.validate_data()
        
        print(f"填充后完整率: {report2.completion_rate:.1f}%")
        
        # 验证：完整率应该有所提高
        assert report2.completion_rate >= report1.completion_rate
        
        parser.close()
        parser2.close()
    
    def test_required_fields_coverage(self):
        """测试必填字段覆盖所有章节"""
        validator = DataValidator()
        
        # 检查第1-6章的核心Sheet
        expected_sheets = [
            "项目基本信息",  # 第1章
            "备选方案",      # 第2章
            "三线分析",      # 第3章
            "环境影响",      # 第4章
            "功能分区",      # 第5章
            "结论建议",      # 第6章
        ]
        
        for sheet in expected_sheets:
            assert sheet in validator.REQUIRED_FIELDS, f"缺少Sheet定义: {sheet}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])