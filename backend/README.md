# Run live server
`uvicorn main:app --reload`
# Run with PM2
`pm2 start "uvicorn main:app --port 3000" --name backend`
