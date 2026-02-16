"""
Neo4j Database Data Fetch Test
Tests all query methods and displays available data
"""

import os
import dotenv
from botchat import Neo4jHandler, NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

dotenv.load_dotenv()

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_results(results, result_type):
    """Print query results in a formatted way"""
    if not results:
        print(f"  ⚠️  No {result_type} found in database")
        return
    
    print(f"  ✅ Found {len(results)} {result_type}:\n")
    for i, item in enumerate(results, 1):
        print(f"  {i}. {'-'*60}")
        for key, value in item.items():
            # Truncate long values
            if isinstance(value, str) and len(value) > 100:
                value = value[:100] + "..."
            print(f"     {key}: {value}")
    print()

def test_database_connection():
    """Test Neo4j connection and fetch sample data"""
    
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║          Neo4j Database Data Fetch Test                       ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    # Initialize Neo4j handler
    try:
        db = Neo4jHandler(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
        print("✅ Neo4j Connection Established")
        print(f"   URI: {NEO4J_URI}")
        print(f"   User: {NEO4J_USER}")
    except Exception as e:
        print(f"❌ Neo4j Connection Failed: {e}")
        return
    
    try:
        # Test 1: Check database nodes count
        print_section("📊 DATABASE OVERVIEW")
        with db.driver.session() as session:
            try:
                # Try using APOC first (if available)
                result = session.run("""
                    CALL db.labels() YIELD label
                    CALL apoc.cypher.run('MATCH (n:' + label + ') RETURN count(n) as count', {})
                    YIELD value
                    RETURN label, value.count as count
                    ORDER BY count DESC
                """)
                labels = [{"Label": record["label"], "Count": record["count"]} for record in result]
                if labels:
                    print("  Node counts by label:")
                    for item in labels:
                        print(f"    - {item['Label']}: {item['Count']} nodes")
                else:
                    print("  ⚠️  Database appears to be empty!")
            except Exception as e:
                # Fallback if APOC is not available
                print("  Counting nodes (APOC not available, using basic method)...")
                node_counts = {}
                for label in ["Domain", "Skill", "Topic", "Question", "Answer", "Difficulty", 
                             "Company", "CompanyDomain", "CompanyRole", "CompanyQuestion", "Recruiter"]:
                    count_result = session.run(f"MATCH (n:{label}) RETURN count(n) as count")
                    count = count_result.single()["count"]
                    if count > 0:
                        node_counts[label] = count
                
                if node_counts:
                    print("  Node counts:")
                    for label, count in sorted(node_counts.items(), key=lambda x: x[1], reverse=True):
                        print(f"    - {label}: {count} nodes")
                else:
                    print("  ⚠️  Database appears to be empty!")
        
        # Test 2: Fetch questions by domain
        print_section("🔍 TEST 1: Get Questions by Domain")
        test_domains = ["algorithms", "data structures", "programming", "software", "computer"]
        
        for domain in test_domains:
            print(f"\n  Searching for domain containing '{domain}'...")
            results = db.get_questions_by_domain(domain, limit=3)
            if results:
                print_results(results, f"questions in '{domain}'")
                break
        else:
            print("  ⚠️  No results for any test domain")
        
        # Test 3: Fetch questions by skill
        print_section("🔍 TEST 2: Get Questions by Skill")
        test_skills = ["Python", "Java", "JavaScript", "SQL", "C++", "sorting", "arrays"]
        
        for skill in test_skills:
            print(f"\n  Searching for skill containing '{skill}'...")
            results = db.get_questions_by_skill(skill, limit=3)
            if results:
                print_results(results, f"questions for skill '{skill}'")
                break
        else:
            print("  ⚠️  No results for any test skill")
        
        # Test 4: Fetch questions by topic
        print_section("🔍 TEST 3: Get Questions by Topic")
        test_topics = ["sorting", "searching", "trees", "graphs", "arrays", "strings"]
        
        for topic in test_topics:
            print(f"\n  Searching for topic containing '{topic}'...")
            results = db.get_questions_by_topic(topic, limit=3)
            if results:
                print_results(results, f"questions for topic '{topic}'")
                break
        else:
            print("  ⚠️  No results for any test topic")
        
        # Test 5: Fetch questions by company
        print_section("🔍 TEST 4: Get Questions by Company")
        test_companies = ["Google", "Amazon", "Microsoft", "Apple", "Facebook", "Meta", "Netflix"]
        
        for company in test_companies:
            print(f"\n  Searching for company containing '{company}'...")
            results = db.get_questions_by_company(company, limit=3)
            if results:
                print_results(results, f"questions from '{company}'")
                break
        else:
            print("  ⚠️  No results for any test company")
        
        # Test 6: Fetch questions by difficulty
        print_section("🔍 TEST 5: Get Questions by Difficulty")
        test_difficulties = ["Easy", "Medium", "Hard", "easy", "medium", "hard"]
        
        for difficulty in test_difficulties:
            print(f"\n  Searching for difficulty '{difficulty}'...")
            results = db.get_questions_by_difficulty(difficulty, limit=3)
            if results:
                print_results(results, f"'{difficulty}' questions")
                break
        else:
            print("  ⚠️  No results for any difficulty level")
        
        # Test 7: Sample all domains
        print_section("📋 ALL AVAILABLE DOMAINS")
        with db.driver.session() as session:
            result = session.run("MATCH (d:Domain) RETURN d.name as name, d.domain_id as id LIMIT 10")
            domains = [{"Name": r["name"], "ID": r["id"]} for r in result]
            if domains:
                print("  Available domains in database:")
                for item in domains:
                    print(f"    - {item['Name']} (ID: {item['ID']})")
            else:
                print("  ⚠️  No domains found")
        
        # Test 8: Sample all skills
        print_section("🛠️  ALL AVAILABLE SKILLS")
        with db.driver.session() as session:
            result = session.run("MATCH (s:Skill) RETURN s.name as name, s.skill_id as id LIMIT 10")
            skills = [{"Name": r["name"], "ID": r["id"]} for r in result]
            if skills:
                print("  Available skills in database:")
                for item in skills:
                    print(f"    - {item['Name']} (ID: {item['ID']})")
            else:
                print("  ⚠️  No skills found")
        
        # Test 9: Sample all companies
        print_section("🏢 ALL AVAILABLE COMPANIES")
        with db.driver.session() as session:
            result = session.run("MATCH (c:Company) RETURN c.name as name, c.company_id as id LIMIT 10")
            companies = [{"Name": r["name"], "ID": r["id"]} for r in result]
            if companies:
                print("  Available companies in database:")
                for item in companies:
                    print(f"    - {item['Name']} (ID: {item['ID']})")
            else:
                print("  ⚠️  No companies found")
        
        # Test 10: Sample questions
        print_section("❓ SAMPLE QUESTIONS")
        with db.driver.session() as session:
            result = session.run("""
                MATCH (q:Question)
                RETURN q.question_id as id, q.title as title, q.description as description
                LIMIT 5
            """)
            questions = []
            for r in result:
                questions.append({
                    "ID": r["id"],
                    "Title": r["title"],
                    "Description": r["description"][:100] + "..." if r["description"] and len(r["description"]) > 100 else r["description"]
                })
            
            if questions:
                print(f"  Found {len(questions)} sample questions:")
                for i, q in enumerate(questions, 1):
                    print(f"\n  {i}. Question ID: {q['ID']}")
                    print(f"     Title: {q['Title']}")
                    if q['Description']:
                        print(f"     Description: {q['Description']}")
            else:
                print("  ⚠️  No questions found in database")
        
        # Final summary
        print_section("📊 TEST SUMMARY")
        print("  ✅ All query methods tested")
        print("  ✅ Neo4j connection working")
        print("\n  💡 Recommendations:")
        print("     - If no data found, check if database has been populated")
        print("     - Verify .cypher files have been executed")
        print("     - Check schema matches the query patterns\n")
    
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()
        print("\n🔒 Closed database connection")

if __name__ == "__main__":
    test_database_connection()
