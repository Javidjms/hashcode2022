import sys
import itertools
import random


class Contributor():
    def __init__(self, id, name, skills_count):
        self.id = id
        self.name = name
        self.skills_count = skills_count
        self.skills = []

    def add_skill(self, skill):
        self.skills.append(skill)

    def level_up_skill(self, skill):
        index = 0
        for s in self.skills:
            if s[0] == skill:
                self.skills[index] = (s[0], s[1]+1)
            index += 1

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
        roles_count,
    ):
        self.id = id
        self.name = name
        self.duration_days = duration_days
        self.score = score
        self.best_before_day = best_before_day
        self.roles_count = roles_count
        self.roles = []
        self.assign_dict = dict()

    def add_role(self, role):
        self.roles.append(role)

    def assign(self, contributor, role):
        self.assign_dict[role] = contributor

    def is_complete(self):
        return len(self.roles) == len(self.assign_dict.keys())

    def can_assign(self, contributor):
        skills = contributor.skills
        for skill in skills:
            for role in self.roles:
                if skill[0] == role[0] and skill[1] >= role[1]:
                    contributor
                    return role[0]
                if skill[0] == role[0] and skill[1] == role[1]-1:
                    for temp_contributor in self.assign_dict.values():
                        temp_skills = temp_contributor.skills
                        if temp_skills[0] == role[0] and temp_skills[1] >= role[1]:
                            return role[0]
        return None

    def __repr__(self):
        return "Project: #{}".format(self.name)


def parse_file(filename):
    with open(filename) as f:
        (
            contributors_count,
            projects_count,
        ) = list(map(int, f.readline().strip().split(' ')))

        # Generate skills
        skills = set()

        # Generate contributors
        contributors = dict()
        for c in range(contributors_count):
            next_line = f.readline().strip().split(' ')
            (constributor_name, skills_count) = next_line
            skills_count = int(skills_count)
            contributor = Contributor(
                c,
                constributor_name,
                skills_count,
            )
            contributors[c] = contributor
            for s in range(skills_count):
                next_line = f.readline().strip().split(' ')
                (skill_name, skill_level) = next_line
                skill_level = int(skill_level)
                skills.add(skill_name)
                contributor.add_skill((skill_name, skill_level))

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
            roles_count = int(roles_count)
            project = Project(
                p,
                project_name,
                duration_days,
                score,
                best_before_day,
                roles_count,
            )
            projects[p] = project
            for r in range(roles_count):
                next_line = f.readline().strip().split(' ')
                (skill_name, skill_level) = next_line
                skill_level = int(skill_level)
                skills.add(skill_name)
                project.add_role((skill_name, skill_level))
    return (
        skills,
        contributors,
        projects,
    )


def solve_dummy(contributors, projects):
    output = list()
    for project_id in projects:
        is_completed = False
        project = projects[project_id]
        for contributor_id in contributors:
            contributor = contributors[contributor_id]
            assign_role = project.can_assign(contributor)
            if assign_role:
                project.assign(contributor, assign_role)

            if project.is_complete():
                is_completed = True
                break

        if is_completed:
            output.append(project)
            continue
    return output


def solve_sorted(contributors, projects):
    output = list()
    sorted_projects = sorted(
        projects,
        key=lambda p: (projects[p].score),
    )
    for project_id in sorted_projects:
        is_completed = False
        project = projects[project_id]
        for contributor_id in contributors:
            contributor = contributors[contributor_id]
            assign_role = project.can_assign(contributor)
            if assign_role:
                project.assign(contributor, assign_role)

            if project.is_complete():
                is_completed = True
                break

        if is_completed:
            output.append(project)
            continue
    return output


def solve_smart(contributors, projects):
    output = list()

    sorted_contributors = sorted(
        contributors,
        key=lambda c: (sum([s[1] for s in contributors[c].skills])),
    )
    sorted_projects = sorted(
        projects,
        key=lambda p: (0 -(projects[p].score/projects[p].duration_days)),
    )
    for project_id in sorted_projects:
        is_completed = False
        project = projects[project_id]
        for contributor_id in sorted_contributors:
            contributor = contributors[contributor_id]
            assign_role = project.can_assign(contributor)
            if assign_role:
                project.assign(contributor, assign_role)

            if project.is_complete():
                for temp_role, temp_contributor in project.assign_dict.items():
                    temp_contributor.level_up_skill(temp_role)
                is_completed = True
                break

        if is_completed:
            output.append(project)
            continue
    return output


def solve_new(contributors, projects):
    # TODO Not finished
    output = list()

    sorted_contributors = sorted(
        contributors,
        key=lambda c: (max([s[1] for s in contributors[c].skills])),
    )
    sorted_projects = sorted(
        projects,
        key=lambda p: (projects[p].best_before_day),
    )
    current_day = 0

    for project_id in sorted_projects:
        project = projects[project_id]

        secondary = dict()
        is_completed = False
        for contributor_id in sorted_contributors:
            contributor = contributors[contributor_id]
            assign_role = project.can_assign(contributor)

            if assign_role:
                project.assign(contributor, assign_role)
                for skA, skB in contributor.skills:
                    secondary[skA] = skB

            if project.is_complete():
                # for temp_role, temp_contributor in project.assign_dict.items():
                    # temp_contributor.level_up_skill(temp_role)
                is_completed = True
                break

        if is_completed:
            output.append(project)
            continue
    return output


def write_file(results, filename):
    with open(filename, 'w') as f:
        f.write('{}\n'.format(len(results)))
        for project in results:
            f.write('{}\n'.format(project.name))
            contributors = []
            for role in project.roles:
                contributors.append(project.assign_dict[role[0]])
            contributors_names = [c.name for c in contributors]
            str_contributors_names = ' '.join(contributors_names)
            f.write('{}\n'.format(str_contributors_names))


def main():
    if len(sys.argv) < 3:
        sys.exit('Syntax: %s <filename> <output>' % sys.argv[0])

    print('Running on file: %s' % sys.argv[1])
    (
        skills,
        contributors,
        projects,
    ) = parse_file(sys.argv[1])
    print('CONFIG', len(skills), len(contributors), len(projects))
    try:
        results = solve_new(contributors, projects)
        print('NB PROJECTS', sys.argv[1], len(results))
    except KeyboardInterrupt:
        pass

    write_file(results, sys.argv[2])


if __name__ == '__main__':
    main()
