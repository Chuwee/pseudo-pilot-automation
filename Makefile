# Pseudo-Pilot Automation - Service Management
# Makefile for managing all project services

.PHONY: help service-up service-down service-restart service-status service-logs redis-up redis-down redis-status redis-logs redis-cli clean

# Colors for output
GREEN := \033[0;32m
RED := \033[0;31m
YELLOW := \033[1;33m
BLUE := \033[0;34m
CYAN := \033[0;36m
NC := \033[0m # No Color

# Configuration
REDIS_CONTAINER := pseudo-pilot-redis
COMPOSE_FILE := docker-compose.yml

#===============================================================================
# HELP
#===============================================================================

help: ## Show this help message
	@echo "$(CYAN)Pseudo-Pilot Automation - Service Manager$(NC)"
	@echo ""
	@echo "$(BLUE)Main Commands:$(NC)"
	@echo "  make service-up         Start all services"
	@echo "  make service-down       Stop all services"
	@echo "  make service-restart    Restart all services"
	@echo "  make service-status     Show status of all services"
	@echo "  make service-logs       Follow logs from all services"
	@echo ""
	@echo "$(BLUE)Redis Commands:$(NC)"
	@echo "  make redis-up           Start Redis only"
	@echo "  make redis-down         Stop Redis only"
	@echo "  make redis-status       Show Redis status"
	@echo "  make redis-logs         Show Redis logs"
	@echo "  make redis-cli          Open Redis CLI"
	@echo ""
	@echo "$(BLUE)Utility:$(NC)"
	@echo "  make clean              Stop all services and remove volumes"
	@echo "  make help               Show this help"

#===============================================================================
# ALL SERVICES
#===============================================================================

service-up: ## Start all services
	@echo "$(GREEN)Starting all services...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) up -d
	@echo "$(GREEN)✓ All services started$(NC)"
	@make service-status

service-down: ## Stop all services
	@echo "$(YELLOW)Stopping all services...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) down
	@echo "$(GREEN)✓ All services stopped$(NC)"

service-restart: ## Restart all services
	@echo "$(YELLOW)Restarting all services...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) restart
	@echo "$(GREEN)✓ All services restarted$(NC)"
	@make service-status

service-status: ## Show status of all services
	@echo "$(CYAN)┌──────────────────────────────────────────────────────────┐$(NC)"
	@echo "$(CYAN)│  PSEUDO-PILOT AUTOMATION - SERVICE STATUS               │$(NC)"
	@echo "$(CYAN)└──────────────────────────────────────────────────────────┘$(NC)"
	@echo ""
	@echo "Service Tree:"
	@echo "├─ $(CYAN)pseudo-pilot-automation$(NC)"
	@echo "│"
	@if docker ps --format '{{.Names}}' | grep -q "^$(REDIS_CONTAINER)$$"; then \
		PID=$$(docker inspect -f '{{.State.Pid}}' $(REDIS_CONTAINER) 2>/dev/null || echo "N/A"); \
		UPTIME=$$(docker ps --filter "name=$(REDIS_CONTAINER)" --format '{{.Status}}' | sed 's/Up //'); \
		echo "│  ├─ $(GREEN)●$(NC) redis-database      [PID: $$PID]"; \
		echo "│  │  └─ Status: $(GREEN)running$(NC) ($$UPTIME)"; \
	else \
		echo "│  ├─ $(RED)●$(NC) redis-database      [PID: ---]"; \
		echo "│  │  └─ Status: $(RED)stopped$(NC)"; \
	fi
	@echo "│  │"
	@echo "│  ├─ $(YELLOW)○$(NC) flightgear         [PID: ---]"
	@echo "│  │  └─ Status: $(YELLOW)not implemented$(NC)"
	@echo "│  │"
	@echo "│  ├─ $(YELLOW)○$(NC) context-database   [PID: ---]"
	@echo "│  │  └─ Status: $(YELLOW)not implemented$(NC)"
	@echo "│  │"
	@echo "│  └─ $(YELLOW)○$(NC) listener-process   [PID: ---]"
	@echo "│     └─ Status: $(YELLOW)not implemented$(NC)"
	@echo "│"
	@echo "└─ $(BLUE)Legend:$(NC) $(GREEN)●$(NC) Running  $(RED)●$(NC) Stopped  $(YELLOW)○$(NC) Not Implemented"
	@echo ""

service-logs: ## Follow logs from all services
	@docker-compose -f $(COMPOSE_FILE) logs -f

#===============================================================================
# REDIS SERVICE
#===============================================================================

redis-up: ## Start Redis service
	@echo "$(GREEN)Starting Redis...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) up -d redis
	@sleep 2
	@if docker exec $(REDIS_CONTAINER) redis-cli ping > /dev/null 2>&1; then \
		echo "$(GREEN)✓ Redis started and responding$(NC)"; \
	else \
		echo "$(RED)✗ Redis started but not responding$(NC)"; \
	fi

redis-down: ## Stop Redis service
	@echo "$(YELLOW)Stopping Redis...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) stop redis
	@echo "$(GREEN)✓ Redis stopped$(NC)"

redis-status: ## Show Redis status and info
	@echo "$(CYAN)════════════════════════════════════════$(NC)"
	@echo "$(CYAN)        Redis Database Status$(NC)"
	@echo "$(CYAN)════════════════════════════════════════$(NC)"
	@echo ""
	@if docker ps --format '{{.Names}}' | grep -q "^$(REDIS_CONTAINER)$$"; then \
		echo "$(GREEN)● Running$(NC)"; \
		echo ""; \
		docker exec $(REDIS_CONTAINER) redis-cli INFO | grep -E "^redis_version:|^uptime_in_days:|^connected_clients:|^used_memory_human:|^total_commands_processed:" | \
			sed 's/redis_version:/  Version: /; s/uptime_in_days:/  Uptime (days): /; s/connected_clients:/  Clients: /; s/used_memory_human:/  Memory: /; s/total_commands_processed:/  Commands: /'; \
	else \
		echo "$(RED)● Stopped$(NC)"; \
		echo ""; \
		echo "Use 'make redis-up' to start Redis"; \
	fi
	@echo ""

redis-logs: ## Show Redis logs
	@docker-compose -f $(COMPOSE_FILE) logs -f redis

redis-cli: ## Open Redis CLI
	@if docker ps --format '{{.Names}}' | grep -q "^$(REDIS_CONTAINER)$$"; then \
		docker exec -it $(REDIS_CONTAINER) redis-cli; \
	else \
		echo "$(RED)Redis is not running. Start it with 'make redis-up'$(NC)"; \
	fi

#===============================================================================
# FLIGHTGEAR SERVICE
#===============================================================================

flightgear-up: ## Start FlightGear service
	@echo "$(GREEN)Starting FlightGear...$(NC)"
	@if fgfs --telnet=5050 --httpd=5000 --disable-ai > /dev/null 2>&1; then \
		echo "$(GREEN)✓ FlightGear started and responding$(NC)"; \
	else \
		echo "$(RED)✗ FlightGear started but not responding$(NC)"; \
	fi

flightgear-status: ## Show FlightGear status and info
	@echo "$(CYAN)════════════════════════════════════════$(NC)"
	@echo "$(CYAN)        Redis Database Status$(NC)"
	@echo "$(CYAN)════════════════════════════════════════$(NC)"
	@echo ""
	@if docker ps --format '{{.Names}}' | grep -q "^$(REDIS_CONTAINER)$$"; then \
		echo "$(GREEN)● Running$(NC)"; \
		echo ""; \
		docker exec $(REDIS_CONTAINER) redis-cli INFO | grep -E "^redis_version:|^uptime_in_days:|^connected_clients:|^used_memory_human:|^total_commands_processed:" | \
			sed 's/redis_version:/  Version: /; s/uptime_in_days:/  Uptime (days): /; s/connected_clients:/  Clients: /; s/used_memory_human:/  Memory: /; s/total_commands_processed:/  Commands: /'; \
	else \
		echo "$(RED)● Stopped$(NC)"; \
		echo ""; \
		echo "Use 'make redis-up' to start Redis"; \
	fi
	@echo ""

redis-logs: ## Show Redis logs
	@docker-compose -f $(COMPOSE_FILE) logs -f redis

redis-cli: ## Open Redis CLI
	@if docker ps --format '{{.Names}}' | grep -q "^$(REDIS_CONTAINER)$$"; then \
		docker exec -it $(REDIS_CONTAINER) redis-cli; \
	else \
		echo "$(RED)Redis is not running. Start it with 'make redis-up'$(NC)"; \
	fi

#===============================================================================
# UTILITY
#===============================================================================

clean: ## Stop all services and remove volumes
	@echo "$(YELLOW)Stopping all services and removing volumes...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) down -v
	@echo "$(GREEN)✓ All services stopped and volumes removed$(NC)"
