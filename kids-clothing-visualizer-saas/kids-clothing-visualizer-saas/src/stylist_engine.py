#!/usr/bin/env python3
"""
童装搭配推理解析引擎 — 核心规则引擎

根据用户输入的孩子信息+场合，自动生成结构化搭配方案。
底层依赖 clothing_rules.md 知识库。
"""

import os
import re
from typing import Optional, Dict, List, Tuple


class StylistEngine:
    """童装搭配推理解析引擎"""

    def __init__(self, rules_path: str = None):
        self.rules_path = rules_path or os.path.join(
            os.path.dirname(__file__), "../references/clothing_rules.md"
        )
        self._rules_cache = None

    def recommend(self, age: int, gender: str, weight_kg: float = None,
                  height_cm: int = None, body_type: str = "标准",
                  season: str = None, occasion: str = None,
                  temperature: str = None) -> Dict:
        """
        生成完整搭配方案

        参数:
            age: 年龄
            gender: 男童/女童
            weight_kg: 体重(kg)
            height_cm: 身高(cm)
            body_type: 偏胖/偏瘦/标准/特殊
            season: 春/夏/秋/冬
            occasion: 上学/运动/派对/旅行/春游/爬山/打水仗/婚礼等
            temperature: 温度范围，如"12-22"

        返回:
            dict: 包含搭配方案、安全提醒、温度建议等
        """
        # 季节推断
        if not season:
            season = self._infer_season()

        # 温度推断
        if not temperature:
            temperature = self._default_temp(season)

        # 体型描述
        body_desc = self._describe_body(age, weight_kg, height_cm, body_type)

        # 生成搭配方案
        plan = self._generate_plan(age, gender, body_type, season, occasion, temperature)

        # 安全自检
        safety = self._safety_check(age, plan)

        # 色彩方案
        colors = self._color_scheme(season, gender, occasion)

        return {
            "child_info": {
                "age": age,
                "gender": gender,
                "weight_kg": weight_kg,
                "height_cm": height_cm,
                "body_type": body_type,
                "body_desc": body_desc
            },
            "environment": {
                "season": season,
                "occasion": occasion,
                "temperature": temperature
            },
            "outfit_plan": plan,
            "safety_notes": safety,
            "color_scheme": colors,
            "temperature_guide": self._temp_guide(season, temperature, plan),
            "image_prompt": self._build_image_prompt(
                age, gender, body_desc, season, occasion, plan, colors
            )
        }

    def _infer_season(self) -> str:
        """根据当前月份推断季节"""
        import datetime
        m = datetime.datetime.now().month
        if 3 <= m <= 5: return "春"
        if 6 <= m <= 8: return "夏"
        if 9 <= m <= 11: return "秋"
        return "冬"

    def _default_temp(self, season: str) -> str:
        temps = {"春": "15-25", "夏": "28-35", "秋": "10-20", "冬": "0-10"}
        return temps.get(season, "15-25")

    def _describe_body(self, age: int, weight: float, height: int, body_type: str) -> str:
        if body_type == "偏胖":
            return f"{age}岁{body_type}，体重{weight}kg身高{height}cm，圆润结实"
        elif body_type == "偏瘦":
            return f"{age}岁{body_type}，体重{weight}kg身高{height}cm，纤细苗条"
        return f"{age}岁标准体型，体重{weight}kg身高{height}cm"

    def _generate_plan(self, age, gender, body_type, season, occasion, temp) -> Dict:
        """生成搭配方案（核心逻辑）"""
        plan = {
            "theme": "",
            "layers": [],
            "shoes": {},
            "accessories": [],
            "bring_items": []
        }

        # 特殊场景优先
        if occasion == "打水仗":
            return self._water_fight_plan(age, gender, body_type)
        elif occasion in ("爬山", "登山", "徒步"):
            return self._hiking_plan(age, gender, body_type, season)
        elif occasion in ("春游", "秋游", "野餐"):
            return self._outing_plan(age, gender, body_type, season)
        elif occasion in ("婚礼", "正式场合", "演出"):
            return self._formal_plan(age, gender, body_type, season)
        elif occasion in ("运动", "体育"):
            return self._sports_plan(age, gender, body_type, season)
        elif occasion in ("上学", "学校", "校园"):
            return self._school_plan(age, gender, body_type, season)
        elif occasion in ("海边", "沙滩", "游泳"):
            return self._beach_plan(age, gender, body_type)

        # 默认：按季节通用方案
        return self._seasonal_plan(age, gender, body_type, season)

    def _water_fight_plan(self, age, gender, body_type) -> Dict:
        return {
            "theme": "夏日水仗·清凉速干风",
            "layers": [
                {"layer": "内裤", "item": "速干平角内裤/泳裤", "color": "深色", "material": "速干面料", "note": "外层打湿不透"},
                {"layer": "上衣", "item": "速干短袖T恤", "color": "亮蓝色", "material": "速干面料(聚酯纤维)", "note": "吸水即干不粘身"},
                {"layer": "下装", "item": "速干运动短裤", "color": "黑色", "material": "速干面料", "note": "膝上长度,松紧腰不勒"},
                {"layer": "鞋子", "item": "溯溪鞋/旧运动鞋", "color": "蓝黑色", "material": "排水网面", "note": "穿旧的!新鞋泡水报废"},
                {"layer": "帽子", "item": "宽檐速干太阳帽", "color": "橙色", "material": "速干面料", "note": "无绳带,防后颈晒伤"}
            ],
            "shoes": {"type": "溯溪鞋/旧运动鞋", "color": "蓝黑色", "note": "提前穿两天磨合"},
            "accessories": ["泳镜(水仗激烈时)", "防水袋装干衣服"],
            "bring_items": ["一套干衣服(含内裤袜子)", "大毛巾", "塑料袋(装湿衣服)", "防晒霜SPF30+", "饮用水"],
            "key_rule": "规则8-7: 速干面料>纯棉! 纯棉吸水变重变冷"
        }

    def _hiking_plan(self, age, gender, body_type, season) -> Dict:
        return {
            "theme": "夏日登山·灵动小探险家",
            "layers": [
                {"layer": "内层", "item": "速干长袖T恤", "color": "浅粉色", "material": "速干面料", "note": "长袖护手臂防刮+防晒"},
                {"layer": "外层", "item": "超轻薄防晒衣(UPF50+)", "color": "白色", "material": "防晒面料", "note": "敞开穿透气,山顶风大拉上"},
                {"layer": "下装", "item": "速干登山长裤", "color": "浅灰色", "material": "速干面料", "note": "防蚊虫+防刮!必须长裤"},
                {"layer": "鞋子", "item": "轻量登山鞋", "color": "白粉色", "material": "防滑橡胶底", "note": "中帮护脚踝,魔术贴"},
                {"layer": "帽子", "item": "宽檐防晒帽", "color": "米色", "material": "UPF面料", "note": "宽檐遮脸后颈,无绳带"}
            ],
            "shoes": {"type": "轻量登山鞋", "color": "白粉色", "note": "提前穿两天磨合"},
            "accessories": ["小容量双肩包", "儿童太阳镜"],
            "bring_items": ["水壶500ml+", "巧克力/能量棒", "防晒霜SPF30+", "驱蚊贴/驱蚊喷雾", "湿巾", "创可贴"],
            "key_rule": "规则8-19至8-24: 旅行穿搭——长裤防蚊防刮"
        }

    def _outing_plan(self, age, gender, body_type, season) -> Dict:
        theme_color = "藏青色" if "男" in (gender or "") else "浅粉色"
        return {
            "theme": f"{'春' if season=='春' else '秋'}日游学·活力运动风",
            "layers": [
                {"layer": "内层", "item": "纯棉长袖T恤", "color": "白色", "material": "精梳棉", "note": "宽松圆领,领口留余量"},
                {"layer": "中层", "item": "落肩连帽卫衣", "color": theme_color, "material": "纯棉抓绒", "note": "落肩加宽肩部,帽绳抽出"},
                {"layer": "外层", "item": "轻薄风衣外套", "color": "亮黄色", "material": "防风面料", "note": "前开拉链,中午热了脱"},
                {"layer": "下装", "item": "直筒运动裤", "color": "深灰色", "material": "纯棉加厚", "note": "宽幅松紧腰,直筒版型"},
                {"layer": "鞋子", "item": "魔术贴运动鞋", "color": "白色", "material": "透气网面", "note": "提前两天磨合"}
            ],
            "shoes": {"type": "魔术贴运动鞋", "color": "白色", "note": "不要穿新鞋出门"},
            "accessories": ["双肩包", "棒球帽"],
            "bring_items": ["备用薄T恤(出汗换)", "水壶", "小零食", "湿巾"],
            "key_rule": "规则9-1: 洋葱式穿搭应对温差"
        }

    def _formal_plan(self, age, gender, body_type, season) -> Dict:
        return {
            "theme": "优雅小绅士/小淑女·正式场合风",
            "layers": [
                {"layer": "内层", "item": "纯棉白衬衫/雪纺打底", "color": "白色", "material": "精梳棉"},
                {"layer": "外套", "item": "小西装/针织开衫", "color": "藏青色/浅粉色", "material": "精纺面料"},
                {"layer": "下装", "item": "西裤/百褶裙", "color": "藏青色/米色", "material": "精纺棉", "note": "及膝长度防绊倒"},
                {"layer": "鞋子", "item": "小皮鞋/芭蕾鞋", "color": "黑色/白色", "note": "防滑鞋底"}
            ],
            "shoes": {"type": "小皮鞋/芭蕾鞋", "color": "黑色/白色", "note": "选软底防滑款"},
            "accessories": ["小领结/领花", "发带/发箍"],
            "bring_items": ["备用袜子(长时间穿皮鞋)", "小零食"],
            "key_rule": "规则8-14至8-18: 正式场合穿搭规则"
        }

    def _sports_plan(self, age, gender, body_type, season) -> Dict:
        return {
            "theme": "活力运动风",
            "layers": [
                {"layer": "上衣", "item": "速干运动T恤", "color": "荧光色", "material": "速干面料", "note": "吸汗速干"},
                {"layer": "下装", "item": "运动短裤/紧身裤+短裤", "color": "黑色", "material": "高弹速干", "note": "含内衬防走光"},
                {"layer": "鞋子", "item": "专业运动鞋", "color": "白黑色", "note": "按运动类型选"}
            ],
            "shoes": {"type": "专业运动鞋", "color": "白黑色", "note": "按运动类型选择"},
            "accessories": ["发带/吸汗带", "运动水壶"],
            "bring_items": ["干毛巾", "备用T恤"],
            "key_rule": "规则8-7至8-13: 运动穿搭规则"
        }

    def _school_plan(self, age, gender, body_type, season) -> Dict:
        return {
            "theme": "校园日常·学院风",
            "layers": [
                {"layer": "上衣", "item": "Polo衫/衬衫领T恤", "color": "白色/浅蓝", "material": "精梳棉", "note": "比圆领正式"},
                {"layer": "下装", "item": "卡其裤/运动裤", "color": "卡其色/藏青", "material": "斜纹棉", "note": "直筒版型"},
                {"layer": "外套", "item": "连帽卫衣(可脱卸)", "color": "藏青色", "material": "棉质", "note": "课间穿脱方便"},
                {"layer": "鞋子", "item": "小白鞋/帆布鞋", "color": "白色", "note": "耐磨防滑"}
            ],
            "shoes": {"type": "小白鞋/帆布鞋", "color": "白色", "note": "耐磨防滑"},
            "accessories": ["书包", "运动水壶"],
            "bring_items": ["体育课备用运动鞋", "雨衣(雨天)"],
            "key_rule": "规则8-1至8-6: 上学穿搭"
        }

    def _beach_plan(self, age, gender, body_type) -> Dict:
        return {
            "theme": "海滩夏日·清凉玩水风",
            "layers": [
                {"layer": "泳衣", "item": "连体泳衣/泳裤+防晒泳衣", "color": "亮色(蓝/橙)", "material": "锦纶+氨纶", "note": "长袖UPF50+防晒泳衣"},
                {"layer": "外层", "item": "速干防晒罩衫", "color": "白色", "material": "速干网面", "note": "上岸后披上防晒"},
                {"layer": "下装", "item": "速干短裤", "color": "亮色", "material": "速干面料"},
                {"layer": "鞋子", "item": "沙滩鞋/洞洞鞋", "color": "亮色", "note": "防烫脚+防贝壳割伤"}
            ],
            "shoes": {"type": "沙滩鞋/洞洞鞋", "color": "亮色", "note": "防烫脚割伤"},
            "accessories": ["宽檐太阳帽", "儿童太阳镜"],
            "bring_items": ["大毛巾", "防晒霜(防水SPF50+)", "饮用水", "干净衣服一套"],
            "key_rule": "规则8-12: 游泳选连体泳衣,户外选长袖防晒泳衣"
        }

    def _seasonal_plan(self, age, gender, body_type, season) -> Dict:
        plans = {
            "春": {"theme": "春日清新·温暖过渡", "colors": "淡粉/鹅黄/嫩绿/天蓝"},
            "夏": {"theme": "夏日清爽·凉感透气", "colors": "白色/浅蓝/柠檬黄/薄荷绿"},
            "秋": {"theme": "秋日暖阳·叠穿过", "colors": "卡其/棕/酒红/姜黄/橄榄绿"},
            "冬": {"theme": "冬日暖绒·保暖分层", "colors": "深蓝/酒红/墨绿/灰色"}
        }
        p = plans.get(season, plans["春"])
        return {
            "theme": p["theme"],
            "seasonal_colors": p["colors"],
            "key_rule": f"规则9: 四季穿搭规则——{season}季"
        }

    def _safety_check(self, age: int, plan: Dict) -> List[str]:
        notes = []
        if age <= 7:
            notes.append("⚠️ 7岁以下儿童服装头颈部严禁任何绳带（规则1-5）")
        if age <= 3:
            notes.append("⚠️ 3岁以下婴幼儿不应存在≤3mm的小配件（规则1-8）")
        notes.append("✅ 摸后颈判断冷热——温暖干燥=刚好，不要摸手脚判断（规则3-6）")
        notes.append("✅ 做举手+弯腰+下蹲测试确保活动自由（规则4-1至4-4）")
        return notes

    def _color_scheme(self, season: str, gender: str, occasion: str) -> Dict:
        return {
            "春": {"main": ["淡粉", "鹅黄", "嫩绿", "天蓝"], "neutral": ["白", "米色"], "accent": ["亮黄", "珊瑚红"]},
            "夏": {"main": ["白", "浅蓝", "柠檬黄"], "neutral": ["卡其", "浅灰"], "accent": ["荧光绿", "珊瑚橙"]},
            "秋": {"main": ["卡其", "棕", "酒红", "姜黄"], "neutral": ["米色", "驼色"], "accent": ["南瓜橙", "砖红"]},
            "冬": {"main": ["深蓝", "酒红", "墨绿", "灰"], "neutral": ["米色", "驼色"], "accent": ["红", "金"]}
        }.get(season, {})

    def _temp_guide(self, season, temp_range, plan) -> List[str]:
        return [
            f"当日预计气温: {temp_range}℃",
            "早上出门可穿全部层数,中午热了逐层脱下",
            "备用一件薄外套在包里,下午起风穿上"
        ]

    def _build_image_prompt(self, age, gender, body_desc, season, occasion, plan, colors) -> str:
        """构建AI生图的提示词"""
        gender_en = "boy" if "男" in (gender or "") else "girl"
        scene_map = {
            "春游": "park with cherry blossoms and green grass",
            "爬山": "mountain trail with green trees and wildflowers",
            "打水仗": "sunny school playground with water splashes",
            "运动": "sports field with grass",
            "上学": "school campus with modern buildings",
            "婚礼": "elegant wedding venue with flowers",
            "海边": "sandy beach with ocean waves",
            "旅行": "scenic outdoor landscape"
        }
        scene = scene_map.get(occasion, "pleasant outdoor setting")

        layers_desc = []
        for l in plan.get("layers", []):
            if l["layer"] in ("上衣", "内层", "中层", "外层"):
                layers_desc.append(f"- {l['layer']}: {l['color']} {l['item']}, {l.get('material','')}")
            elif l["layer"] == "下装":
                layers_desc.append(f"- Bottom: {l['color']} {l['item']}, {l.get('material','')}")
            elif l["layer"] == "鞋子":
                layers_desc.append(f"- Shoes: {l['color']} {l['item']}")

        return f"""Full-body front view of a {age}-year-old {gender_en}, {body_desc}, wearing a {season} {occasion} outfit in a {scene}.
{chr(10).join(layers_desc)}
The child is standing naturally, looking forward with a gentle smile.
{scene.capitalize()} background, soft natural lighting.
Style: realistic clothing catalog photography, clean background with subtle scene context, professional lighting, full-body shot, sharp focus on all outfit details, product photography quality, high resolution, ultra-detailed, 8k."""


# CLI 演示
if __name__ == "__main__":
    engine = StylistEngine()

    # 测试用例
    test_cases = [
        {"age": 7, "gender": "男童", "weight_kg": 27.5, "height_cm": 130,
         "body_type": "偏胖", "season": "春季", "occasion": "春游"},
        {"age": 7, "gender": "男童", "weight_kg": 27.5, "height_cm": 130,
         "body_type": "偏胖", "season": "夏季", "occasion": "打水仗"},
        {"age": 7, "gender": "女童", "weight_kg": 20, "height_cm": 120,
         "body_type": "偏瘦", "season": "夏季", "occasion": "爬山"},
    ]

    for i, tc in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"测试 {i}: {tc['age']}岁{tc['gender']} {tc['occasion']}")
        print(f"{'='*60}")
        result = engine.recommend(**tc)
        print(f"主题: {result['outfit_plan'].get('theme','')}")
        print(f"安全提醒: {result['safety_notes'][0] if result['safety_notes'] else ''}")
