# Neo4j Data Requirements

This project uses two Neo4j schema/seed scripts:

- [company.cypher](company.cypher)
- [question.cypher](question.cypher)

## 1) `company.cypher`

### Required parameters
Provide the following parameters when running the script:

- `company_id`
- `company_name`
- `headquarters`
- `founded_year`
- `company_type`

- `company_domain_id`
- `domain_name`
- `domain_description`

- `role_id`
- `role_name`
- `role_level`
- `role_description`

- `comp_question_id`
- `comp_question_title`
- `question_type`
- `difficulty`
- `year_asked`
- `question_id`

- `recruiter_id`
- `recruiter_name`
- `recruiter_email`
- `designation`

### Nodes created
- `Company`
- `CompanyDomain`
- `CompanyRole`
- `CompanyQuestion`
- `Recruiter`

### Relationships created
- `(Company)-[:HAS_DOMAIN]->(CompanyDomain)`
- `(CompanyDomain)-[:HAS_ROLE]->(CompanyRole)`
- `(CompanyRole)-[:ASKS_QUESTION]->(CompanyQuestion)`
- `(CompanyDomain)-[:HAS_RECRUITER]->(Recruiter)`


## 2) `question.cypher`

### Required parameters
Provide the following parameters when running the script:

- `list_id`
- `list_name`
- `list_description`

- `domain_id`
- `domain_name`
- `domain_description`

- `skill_id`
- `skill_name`
- `skill_description`

- `topic_id`
- `topic_name`
- `topic_description`

- `difficulty_id`
- `difficulty_level`

- `question_id`
- `question_title`
- `question_description`
- `question_hints`
- `question_example`
- `company_ids` (array of strings)

- `answer_id`
- `answer_explanation`
- `answer_code`
- `code_explanation`

### Nodes created
- `QuestionList`
- `Domain`
- `Skill`
- `Topic`
- `Difficulty`
- `Question`
- `Answer`

### Relationships created
- `(QuestionList)-[:HAS_DOMAIN]->(Domain)`
- `(Domain)-[:HAS_SKILL]->(Skill)`
- `(Skill)-[:HAS_TOPIC]->(Topic)`
- `(Topic)-[:HAS_DIFFICULTY]->(Difficulty)`
- `(Difficulty)-[:HAS_QUESTION]->(Question)`
- `(Question)-[:HAS_ANSWER]->(Answer)`