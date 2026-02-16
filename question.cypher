////////////////////////////////////////////////////////////////////////
///////////////////// OPTIONAL DATABASE RESET //////////////////////////
////////////////////////////////////////////////////////////////////////

// ⚠ UNCOMMENT ONLY IF YOU WANT CLEAN START
// MATCH (n) DETACH DELETE n;


////////////////////////////////////////////////////////////////////////
///////////////////// 1️⃣ UNIQUE CONSTRAINTS ////////////////////////////
////////////////////////////////////////////////////////////////////////

CREATE CONSTRAINT question_list_id_unique IF NOT EXISTS
FOR (ql:QuestionList)
REQUIRE ql.list_id IS UNIQUE;

CREATE CONSTRAINT domain_id_unique IF NOT EXISTS
FOR (d:Domain)
REQUIRE d.domain_id IS UNIQUE;

CREATE CONSTRAINT skill_id_unique IF NOT EXISTS
FOR (s:Skill)
REQUIRE s.skill_id IS UNIQUE;

CREATE CONSTRAINT topic_id_unique IF NOT EXISTS
FOR (t:Topic)
REQUIRE t.topic_id IS UNIQUE;

CREATE CONSTRAINT difficulty_id_unique IF NOT EXISTS
FOR (df:Difficulty)
REQUIRE df.difficulty_id IS UNIQUE;

CREATE CONSTRAINT question_id_unique IF NOT EXISTS
FOR (q:Question)
REQUIRE q.question_id IS UNIQUE;

CREATE CONSTRAINT answer_id_unique IF NOT EXISTS
FOR (a:Answer)
REQUIRE a.answer_id IS UNIQUE;


////////////////////////////////////////////////////////////////////////
///////////////////// 2️⃣ PERFORMANCE INDEXES //////////////////////////
////////////////////////////////////////////////////////////////////////

CREATE INDEX domain_name_index IF NOT EXISTS
FOR (d:Domain)
ON (d.name);

CREATE INDEX skill_name_index IF NOT EXISTS
FOR (s:Skill)
ON (s.name);

CREATE INDEX topic_name_index IF NOT EXISTS
FOR (t:Topic)
ON (t.name);

CREATE INDEX difficulty_level_index IF NOT EXISTS
FOR (df:Difficulty)
ON (df.level);


////////////////////////////////////////////////////////////////////////
///////////////////// 3️⃣ MASTER INSERT TEMPLATE ///////////////////////
////////////////////////////////////////////////////////////////////////

MERGE (ql:QuestionList {list_id: $list_id})
ON CREATE SET
    ql.name = $list_name,
    ql.description = $list_description,
    ql.created_at = datetime()

MERGE (d:Domain {domain_id: $domain_id})
ON CREATE SET
    d.name = $domain_name,
    d.description = $domain_description

MERGE (ql)-[:HAS_DOMAIN]->(d)

MERGE (s:Skill {skill_id: $skill_id})
ON CREATE SET
    s.name = $skill_name,
    s.description = $skill_description

MERGE (d)-[:HAS_SKILL]->(s)

MERGE (t:Topic {topic_id: $topic_id})
ON CREATE SET
    t.name = $topic_name,
    t.description = $topic_description

MERGE (s)-[:HAS_TOPIC]->(t)

MERGE (df:Difficulty {difficulty_id: $difficulty_id})
ON CREATE SET
    df.level = $difficulty_level

MERGE (t)-[:HAS_DIFFICULTY]->(df)

MERGE (q:Question {question_id: $question_id})
ON CREATE SET
    q.title = $question_title,
    q.description = $question_description,
    q.hints = $question_hints,
    q.example = $question_example,
    q.company_ids = $company_ids,
    q.created_at = datetime()
ON MATCH SET
    q.updated_at = datetime(),
    q.company_ids = $company_ids

MERGE (df)-[:HAS_QUESTION]->(q)

MERGE (a:Answer {answer_id: $answer_id})
ON CREATE SET
    a.explanation = $answer_explanation,
    a.code = $answer_code,
    a.code_explanation = $code_explanation

MERGE (q)-[:HAS_ANSWER]->(a);
