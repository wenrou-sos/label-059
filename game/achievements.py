import json
import os
import time


class Achievement:
    def __init__(self, achievement_id, name, description, icon, condition_func=None, condition_params=None):
        self.id = achievement_id
        self.name = name
        self.description = description
        self.icon = icon
        self.condition_func = condition_func
        self.condition_params = condition_params or {}
        self.unlocked = False
        self.unlocked_at = None

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'unlocked': self.unlocked,
            'unlocked_at': self.unlocked_at
        }


class AchievementManager:
    def __init__(self):
        self.achievements = {}
        self.unlocked_count = 0
        self.total_count = 0
        self.callbacks = []
        self.save_path = os.path.join(os.path.dirname(__file__), 'achievements_save.json')

        self.stats = {
            'total_parts_processed': 0,
            'total_parts_correct': 0,
            'total_parts_wrong': 0,
            'max_combo': 0,
            'max_score': 0,
            'max_game_time': 0,
            'assembly_parts': 0,
            'qa_parts': 0,
            'packaging_parts': 0,
            'games_played': 0,
            'max_time_played': 0,
            'perfect_streak_start': 0,
            'no_miss_streak': 0,
            'assembly_parts_this': 0,
            'qa_parts_this': 0,
            'packaging_parts_this': 0,
        }

        self._define_achievements()
        self._load()

    def _define_achievements(self):
        achievements_list = [
            Achievement(
                'first_correct', '初试锋芒',
                '正确放置第一个零件',
                '⭐',
                lambda s: s['total_parts_correct'] >= 1
            ),
            Achievement(
                'combo_5', '五连击',
                '连续正确放置 5 个零件',
                '🔥',
                lambda s: s['max_combo'] >= 5
            ),
            Achievement(
                'combo_10', '十连击',
                '连续正确放置 10 个零件',
                '💥',
                lambda s: s['max_combo'] >= 10
            ),
            Achievement(
                'combo_20', '连击大师',
                '连续正确放置 20 个零件',
                '👑',
                lambda s: s['max_combo'] >= 20
            ),
            Achievement(
                'parts_10', '新手上线',
                '累计正确处理 10 个零件',
                '🔧',
                lambda s: s['total_parts_correct'] >= 10
            ),
            Achievement(
                'parts_50', '熟练工',
                '累计正确处理 50 个零件',
                '⚙️',
                lambda s: s['total_parts_correct'] >= 50
            ),
            Achievement(
                'parts_100', '老师傅',
                '累计正确处理 100 个零件',
                '🏆',
                lambda s: s['total_parts_correct'] >= 100
            ),
            Achievement(
                'assembly_20', '组装能手',
                '累计正确处理 20 个组装工位零件',
                '🔩',
                lambda s: s['assembly_parts'] >= 20
            ),
            Achievement(
                'qa_20', '质检能手',
                '累计正确处理 20 个质检工位零件',
                '🔍',
                lambda s: s['qa_parts'] >= 20
            ),
            Achievement(
                'packaging_20', '包装能手',
                '累计正确处理 20 个包装工位零件',
                '📦',
                lambda s: s['packaging_parts'] >= 20
            ),
            Achievement(
                'time_1min', '按时下班',
                '单局游戏坚持 1 分钟',
                '⏰',
                lambda s: s['max_time_played'] >= 60
            ),
            Achievement(
                'time_3min', '老员工',
                '单局游戏坚持 3 分钟',
                '👨‍🏭',
                lambda s: s['max_time_played'] >= 180
            ),
            Achievement(
                'time_5min', '劳动模范',
                '单局游戏坚持 5 分钟',
                '🏅',
                lambda s: s['max_time_played'] >= 300
            ),
            Achievement(
                'score_100', '百元户',
                '单局得分达到 100 分',
                '💰',
                lambda s: s['max_score'] >= 100
            ),
            Achievement(
                'score_500', '小富翁',
                '单局得分达到 500 分',
                '💎',
                lambda s: s['max_score'] >= 500
            ),
            Achievement(
                'score_1000', '工厂大亨',
                '单局得分达到 1000 分',
                '👑',
                lambda s: s['max_score'] >= 1000
            ),
            Achievement(
                'perfect_start', '完美开局',
                '单局游戏前 10 个零件全部正确',
                '✨',
                lambda s: s['perfect_streak_start'] >= 10
            ),
            Achievement(
                'games_5', '常来常往',
                '累计游玩 5 局',
                '🎮',
                lambda s: s['games_played'] >= 5
            ),
            Achievement(
                'no_miss_50', '精准无误',
                '单局处理 50 个零件且无漏件',
                '🎯',
                lambda s: s['no_miss_streak'] >= 50
            ),
            Achievement(
                'all_types', '全能选手',
                '在一局中每个工位至少处理 10 个零件',
                '🌟',
                lambda s: s['assembly_parts_this'] >= 10 and s['qa_parts_this'] >= 10 and s['packaging_parts_this'] >= 10
            ),
        ]

        for ach in achievements_list:
            self.achievements[ach.id] = ach

        self.total_count = len(achievements_list)

    def add_listener(self, callback):
        self.callbacks.append(callback)

    def remove_listener(self, callback):
        if callback in self.callbacks:
            self.callbacks.remove(callback)

    def update_stat(self, stat_name, value=None, increment=1):
        if value is not None:
            self.stats[stat_name] = value
        else:
            self.stats[stat_name] = self.stats.get(stat_name, 0) + increment

    def check_all(self):
        newly_unlocked = []
        for ach_id, ach in self.achievements.items():
            if not ach.unlocked:
                try:
                    if ach.condition_func and ach.condition_func(self.stats):
                        ach.unlocked = True
                        ach.unlocked_at = time.time()
                        newly_unlocked.append(ach)
                        self.unlocked_count += 1
                        for callback in self.callbacks:
                            try:
                                callback(ach)
                            except Exception:
                                pass
                except Exception:
                    pass
        if newly_unlocked:
            self._save()
        return newly_unlocked

    def get_achievement(self, achievement_id):
        return self.achievements.get(achievement_id)

    def get_all_achievements(self, include_locked=True):
        result = list(self.achievements.values())
        if not include_locked:
            result = [a for a in result if a.unlocked]
        return sorted(result, key=lambda x: (not x.unlocked, x.id))

    def get_progress(self):
        return self.unlocked_count, self.total_count

    def reset_session_stats(self):
        self.stats['perfect_streak_start'] = 0
        self.stats['no_miss_streak'] = 0
        self.stats['assembly_parts_this'] = 0
        self.stats['qa_parts_this'] = 0
        self.stats['packaging_parts_this'] = 0

    def _save(self):
        try:
            ach_data = {}
            for ach_id, ach in self.achievements.items():
                ach_data[ach_id] = {
                    'unlocked': ach.unlocked,
                    'unlocked_at': ach.unlocked_at
                }
            persistent_stats = {}
            for k, v in self.stats.items():
                if k not in ['perfect_streak_start', 'no_miss_streak',
                             'assembly_parts_this', 'qa_parts_this', 'packaging_parts_this']:
                    persistent_stats[k] = v
            data = {
                'achievements': ach_data,
                'stats': persistent_stats
            }
            with open(self.save_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _load(self):
        try:
            if not os.path.exists(self.save_path):
                return
            with open(self.save_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            ach_data = data.get('achievements', {})
            for ach_id, info in ach_data.items():
                if ach_id in self.achievements:
                    self.achievements[ach_id].unlocked = info.get('unlocked', False)
                    self.achievements[ach_id].unlocked_at = info.get('unlocked_at')
                    if info.get('unlocked'):
                        self.unlocked_count += 1
            for k, v in data.get('stats', {}).items():
                self.stats[k] = v
        except Exception:
            pass
