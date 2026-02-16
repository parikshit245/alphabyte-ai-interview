////////////////////////////////////////////////////////////////////////
///////////////////// COMPANY GRAPH SCHEMA FILE ////////////////////////
////////////////////////////////////////////////////////////////////////


////////////////////////////////////////////////////////////////////////
///////////////////// 1️⃣ COMPANY CONSTRAINTS //////////////////////////
////////////////////////////////////////////////////////////////////////

CREATE CONSTRAINT company_id_unique IF NOT EXISTS
FOR (c:Company)
REQUIRE c.company_id IS UNIQUE;

CREATE CONSTRAINT company_domain_id_unique IF NOT EXISTS
FOR (cd:CompanyDomain)
REQUIRE cd.company_domain_id IS UNIQUE;

CREATE CONSTRAINT company_role_id_unique IF NOT EXISTS
FOR (cr:CompanyRole)
REQUIRE cr.role_id IS UNIQUE;

CREATE CONSTRAINT comp_question_id_unique IF NOT EXISTS
FOR (cq:CompanyQuestion)
REQUIRE cq.comp_question_id IS UNIQUE;

CREATE CONSTRAINT recruiter_id_unique IF NOT EXISTS
FOR (r:Recruiter)
REQUIRE r.recruiter_id IS UNIQUE;


////////////////////////////////////////////////////////////////////////
///////////////////// 2️⃣ INDEXES //////////////////////////////////////
////////////////////////////////////////////////////////////////////////

CREATE INDEX company_name_index IF NOT EXISTS
FOR (c:Company) ON (c.name);

CREATE INDEX company_domain_name_index IF NOT EXISTS
FOR (cd:CompanyDomain) ON (cd.name);

CREATE INDEX role_name_index IF NOT EXISTS
FOR (cr:CompanyRole) ON (cr.name);

CREATE INDEX recruiter_name_index IF NOT EXISTS
FOR (r:Recruiter) ON (r.name);


////////////////////////////////////////////////////////////////////////
///////////////////// 3️⃣ COMPANY MASTER INSERT ////////////////////////
////////////////////////////////////////////////////////////////////////

MERGE (c:Company {company_id:$company_id})
ON CREATE SET
    c.name = $company_name,
    c.headquarters = $headquarters,
    c.founded_year = $founded_year,
    c.company_type = $company_type,
    c.created_at = datetime()

MERGE (cd:CompanyDomain {company_domain_id:$company_domain_id})
ON CREATE SET
    cd.name = $domain_name,
    cd.description = $domain_description

MERGE (c)-[:HAS_DOMAIN]->(cd)

MERGE (cr:CompanyRole {role_id:$role_id})
ON CREATE SET
    cr.name = $role_name,
    cr.level = $role_level,
    cr.description = $role_description

MERGE (cd)-[:HAS_ROLE]->(cr)

MERGE (cq:CompanyQuestion {comp_question_id:$comp_question_id})
ON CREATE SET
    cq.title = $comp_question_title,
    cq.question_type = $question_type,
    cq.difficulty = $difficulty,
    cq.year_asked = $year_asked,
    cq.question_id = $question_id,
    cq.created_at = datetime()

MERGE (cr)-[:ASKS_QUESTION]->(cq)

MERGE (r:Recruiter {recruiter_id:$recruiter_id})
ON CREATE SET
    r.name = $recruiter_name,
    r.email = $recruiter_email,
    r.designation = $designation,
    r.created_at = datetime()

MERGE (cd)-[:HAS_RECRUITER]->(r);
