#\!/bin/bash
echo "🔍 Checking for OpenAI API calls in the last 5 minutes..."
docker compose -f docker-compose.test.yml logs backend --since 5m  < /dev/null |  grep -E "(api.openai.com|Background task started|IN_PROGRESS)" | tail -20

echo -e "\n📊 Checking analysis status in database..."
docker compose -f docker-compose.test.yml exec -T postgres psql -U secanalyst -d security_analyst_test -c "SELECT id, status, created_at FROM analyses WHERE created_at > NOW() - INTERVAL '5 minutes' ORDER BY created_at DESC LIMIT 5;"
