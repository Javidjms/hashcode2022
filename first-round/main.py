import sys
import statistics
from collections import defaultdict


def default_to_regular(d):
    if isinstance(d, defaultdict):
        d = {k: default_to_regular(v) for k, v in d.items()}
    return d


class Skill:
    def __init__(self, language, level):
        self.language = language
        self.level = level

    def __repr__(self):
        return "Skill: {} - Lv:{}".format(self.language, self.level)


class Role:
    def __init__(self, language, level):
        self.language = language
        self.level = level
        self.contributor = None
        self.possible_contributor = None

    def __repr__(self):
        return "Role: {} - Lv:{}".format(self.language, self.level)


class Contributor:
    def __init__(self, id, name, skills):
        self.id = id
        self.name = name
        self.available_day = 0

        self.skills = skills
        self.skills_dict = dict()
        for skill in skills:
            self.skills_dict[skill.language] = skill

    def __repr__(self):
        return "Contributor: #{}".format(self.name)


class Project():
    def __init__(
        self,
        id,
        name,
        duration_days,
        score,
        best_before_day,
        roles,
    ):
        self.id = id
        self.name = name
        self.duration_days = duration_days
        self.score = score
        self.best_before_day = best_before_day

        self.roles = roles
        self.possible_mentor_dict = defaultdict(lambda: None)

        self.is_completed = False

        # Create a roles dict
        self.roles_dict = defaultdict(dict)
        for role in roles:
            self.roles_dict[role.language][role.level] = role

    def can_assign(self, contributor):
        for skill in contributor.skills:
            for role in self.roles:
                if role.possible_contributor is not None:
                    continue

                if skill.language == role.language \
                   and skill.level >= role.level:
                    return role

                if skill.language == role.language \
                   and skill.level + 1 == role.level \
                   and self.possible_mentor_dict[role.language] is not None:
                    temp_mentor = self.possible_mentor_dict[role.language]
                    if temp_mentor.skills_dict[role.language].level >= role.level:
                        return role
        return None

    def set_as_possible_contributor(self, contributor, role):
        role.possible_contributor = contributor

        for skill in contributor.skills:
            if skill.language == role.language:
                continue

            for temp_role in self.roles:
                if skill.level >= temp_role.level:
                    current_mentor = self.possible_mentor_dict.get(
                        skill.language,
                        None,
                    )
                    if current_mentor is None \
                       or (
                        contributor.skills_dict[role.language].level >=
                        current_mentor.skills_dict[role.language].level
                       ):
                        self.possible_mentor_dict[skill.language] = contributor

    def assign_possible_contributors(self):
        for role in self.roles:
            role.contributor = role.possible_contributor

            # Increase skill level
            current_skill = role.contributor.skills_dict[role.language]
            if current_skill.level <= role.level:
                current_skill.level += 1

            # Update available day
            role.contributor.available_day += self.duration_days

    def is_fulfilled(self):
        return all([
                role.possible_contributor is not None
                for role in self.roles
            ])

    def __repr__(self):
        return "Project: #{}".format(self.name)


def solve_dummy(contributors, projects):
    output = list()
    for project_id in projects:
        is_completed = False
        project = projects[project_id]
        for contributor_id in contributors:
            contributor = contributors[contributor_id]
            assign_role = project.can_assign(contributor)
            if assign_role:
                project.set_as_possible_contributor(contributor, assign_role)

                if project.is_fulfilled():
                    is_completed = True
                    break

        if is_completed:
            project.assign_possible_contributors()
            output.append(project)
            continue

    return output


def solve_dummy_bis(contributors, projects):
    output = list()
    current_turn = 0
    while True:
        available_projects = {
            key: value
            for key, value in projects.items()
            if not value.is_completed
        }

        available_contributors = {
            key: value
            for key, value in contributors.items()
            if value.available_day <= current_turn
        }

        if len(available_projects.keys()) == 0:
            break

        for project_id in available_projects:
            is_completed = False
            project = projects[project_id]
            for contributor_id in available_contributors:
                contributor = contributors[contributor_id]
                assign_role = project.can_assign(contributor)
                if assign_role:
                    project.set_as_possible_contributor(contributor, assign_role)

                    if project.is_fulfilled():
                        project.is_completed = True
                        is_completed = True
                        break

            if is_completed:
                project.assign_possible_contributors()
                output.append(project)
            else:
                # Reinitialize
                project.possible_mentor_dict = defaultdict(lambda: None)
                for role in project.roles:
                    role.possible_contributor = None

        current_turn += 1

    return output


def solve_hashmap(contributors, projects, max_days):
    completed_projects = list()
    current_turn = 0

    while True:
        min_skip_duration = None
        if current_turn >= max_days:
            break

        available_projects = {
            p: projects[p]
            for p in projects
            if not projects[p].is_completed
        }

        sorted_projects = sorted(
            available_projects,
            key=lambda p: (len(projects[p].roles), sum([r.level for r in projects[p].roles])),
        )

        print('current_turn', current_turn, max_days, len(available_projects))

        if len(available_projects.keys()) == 0:
            break

        for project_id in sorted_projects:
            output_dict = defaultdict(
                lambda: defaultdict(
                    lambda: defaultdict(lambda: list()),
                ),
            )
            project = projects[project_id]

            if project in completed_projects:
                continue

            for role in project.roles:
                output_dict[role.language][role.level]["roles"].append(role)

            available_contributors = {
                c: contributors[c]
                for c in contributors
                if contributors[c].available_day <= current_turn
            }

            sorted_contributors = sorted(
                available_contributors,
                key=lambda c: (-len(contributors[c].skills)),
            )

            for contributor_id in sorted_contributors:
                contributor = contributors[contributor_id]
                for skill in contributor.skills:
                    if project.roles_dict[skill.language]:
                        current_roles = project.roles_dict[skill.language].values()
                        for current_role in current_roles:
                            if skill.level >= current_role.level:
                                output_dict[current_role.language][current_role.level]["primary_contributors"].append(contributor)
                            if skill.level + 1 == current_role.level:
                                output_dict[current_role.language][current_role.level]["secondary_contributors"].append(contributor)

            selected_contributors = set()
            is_break = False
            for values in output_dict.values():
                sorted_values = dict(
                    sorted(values.items(), key=lambda v: len(v[1]["secondary_contributors"])),
                )
                for temp_values in sorted_values.values():
                    roles = temp_values['roles']
                    primary_contributors = set(temp_values['primary_contributors']) - selected_contributors
                    secondary_contributors = set(temp_values['secondary_contributors']) - selected_contributors
                    mentors = primary_contributors.intersection(selected_contributors)

                    total_contributors_count = len(primary_contributors) + len(secondary_contributors)
                    if total_contributors_count >= len(roles):
                        roles_count = len(roles)

                        if len(mentors):
                            temp_contributors = list(secondary_contributors) + list(primary_contributors)

                        else:
                            temp_contributors = list(primary_contributors)
                            if len(temp_contributors) < len(roles):
                                is_break = True
                                break

                        temp_selected_contributors = temp_contributors[:roles_count]
                        selected_contributors.update(temp_selected_contributors)
                        temp_values['selected_contributors'] = temp_selected_contributors
                    else:
                        is_break = True
                        break
                if is_break:
                    break

            if is_break:
                continue

            for values in output_dict.values():
                for temp_values in values.values():
                    roles = temp_values['roles']
                    selected_contributors = temp_values["selected_contributors"]
                    for role, contributor in zip(roles, selected_contributors):
                        role.contributor = contributor

                        # Increase skill level
                        current_skill = contributor.skills_dict[role.language]
                        if current_skill.level <= role.level:
                            current_skill.level += 1

                        # Update available day
                        contributor.available_day += project.duration_days

            project.is_completed = True
            completed_projects.append(project)
            if min_skip_duration:
                min_skip_duration = max(min_skip_duration, project.duration_days)
            else:
                min_skip_duration = project.duration_days

        if min_skip_duration:
            current_turn += min_skip_duration
        else:
            break
    return completed_projects


def parse_file(filename):
    with open(filename) as f:
        (
            contributors_count,
            projects_count,
        ) = list(map(int, f.readline().strip().split(' ')))

        # Generate languages
        languages = set()

        # Generate contributors
        contributors = dict()
        for c in range(contributors_count):
            next_line = f.readline().strip().split(' ')
            (constributor_name, skills_count) = next_line

            # Generate skills
            skills_count = int(skills_count)
            skills = []
            for s in range(skills_count):
                next_line = f.readline().strip().split(' ')
                (skill_name, skill_level) = next_line
                skill_level = int(skill_level)

                languages.add(skill_name)
                skill = Skill(skill_name, skill_level)
                skills.append(skill)

            contributor = Contributor(
                c,
                constributor_name,
                skills,
            )
            contributors[c] = contributor

        # Generate projects
        projects = dict()
        for p in range(projects_count):
            next_line = f.readline().strip().split(' ')
            (
                project_name,
                duration_days,
                score,
                best_before_day,
                roles_count,
            ) = next_line
            duration_days = int(duration_days)
            score = int(score)
            best_before_day = int(best_before_day)

            # Generate roles
            roles = []
            roles_count = int(roles_count)
            for r in range(roles_count):
                next_line = f.readline().strip().split(' ')
                (skill_name, skill_level) = next_line
                skill_level = int(skill_level)

                languages.add(skill_name)
                role = Role(skill_name, skill_level)
                roles.append(role)

            project = Project(
                p,
                project_name,
                duration_days,
                score,
                best_before_day,
                roles,
            )
            projects[p] = project

    # Initialize skills
    for contributor in contributors.values():
        for language in languages:
            if language not in contributor.skills_dict:
                newbie_skill = Skill(language, 0)
                contributor.skills_dict[language] = newbie_skill
    return (
        languages,
        contributors,
        projects,
    )


def write_file(results, filename):
    with open(filename, 'w') as f:
        f.write('{}\n'.format(len(results)))
        for project in results:
            f.write('{}\n'.format(project.name))
            contributors = []
            for role in project.roles:
                contributors.append(role.contributor)
            contributors_names = [c.name for c in contributors]
            str_contributors_names = ' '.join(contributors_names)
            f.write('{}\n'.format(str_contributors_names))


def main():
    if len(sys.argv) < 3:
        sys.exit('Syntax: %s <filename> <output>' % sys.argv[0])

    print('Running on file: %s' % sys.argv[1])
    (
        languages,
        contributors,
        projects,
    ) = parse_file(sys.argv[1])
    print('CONFIG', len(languages), len(contributors), len(projects))
    max_days = max([p.best_before_day for p in projects.values()])
    try:
        results = solve_hashmap(contributors, projects, max_days)
        print('NB PROJECTS', sys.argv[1], len(results))
    except KeyboardInterrupt:
        pass

    # write_file(results, sys.argv[2])


if __name__ == '__main__':
    main()
