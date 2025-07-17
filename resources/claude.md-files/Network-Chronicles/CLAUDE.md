# Network Chronicles Development Notes

## Common Commands
- `chmod +x <script_name>` - Make a script executable
- `./bin/service-discovery.sh $(whoami)` - Run service discovery manually 
- `./nc-discover-services.sh` - Run service discovery wrapper script

## Agentic LLM Integration Implementation Plan

### Goals
- Create an Agentic LLM to act as "The Architect" character
- Add dynamic, personalized interactions with the character
- Ensure interactions are contextually aware of player's progress and discoveries
- Maintain narrative consistency while allowing for dynamic conversations

### Implementation Steps
1. Create a LLM-powered Architect Agent
   - Design a system to communicate with an LLM API (e.g., Claude, GPT)
   - Implement appropriate context management
   - Define character parameters and constraints
   - Create conversation history tracking

2. Build context gathering system
   - Collect player's progress data (discoveries, quests, journal entries)
   - Gather relevant game state information
   - Format context for effective LLM prompting

3. Develop triggering mechanisms
   - Create situations where The Architect can appear
   - Implement terminal-based chat interface
   - Add special encrypted message system

4. Ensure narrative consistency
   - Maintain character voice and motivations
   - Align interactions with game story progression
   - Create guardrails to prevent contradictions

5. Add cryptic messaging capabilities
   - Enable The Architect to provide hints in character
   - Create system for encrypted or hidden messages
   - Implement progressive revelation of information

### Technical Implementation

#### 1. Architect Agent System (`bin/architect-agent.sh`)
- Script to manage communication with LLM API
- Handles context management and prompt construction
- Processes responses and formats them appropriately
- Maintains conversation history in player state

#### 2. Context Manager (`bin/utils/context-manager.sh`)
- Gathers and processes game state for context
- Extracts relevant player discoveries and progress
- Formats information for inclusion in prompts
- Manages context window limitations

#### 3. Terminal Chat Interface (`bin/architect-terminal.sh`)
- Provides retro-themed terminal interface for chatting with The Architect
- Simulates encrypted connection
- Handles input/output with appropriate styling
- Maintains immersion with themed elements

#### 4. Prompt Template System
- Base prompt with character definition and constraints
- Dynamic context injection based on game state
- System for tracking conversation history
- Safety guardrails and response guidelines

### Character Guidelines for The Architect

The Architect should embody these characteristics:
- Knowledgeable but cryptic - never gives direct answers
- Paranoid but methodical - believes they're being monitored
- Technical and precise - speaks like an experienced sysadmin
- Mysterious but helpful - wants to guide the player
- Bound by constraints - can't reveal everything at once

### Technical Requirements
- LLM API access (Claude or similar)
- Context window management
- Conversation history tracking
- Reliable error handling
- Rate limiting and token management

## Enhanced Service Discovery Implementation

### Implementation Summary
We've successfully implemented enhanced service discovery capabilities for Network Chronicles:

1. **Service Detection System**
   - Created `service-discovery.sh` script that safely detects running services on the local machine
   - Implemented detection for common services like web servers, databases, and monitoring systems
   - Added support for identifying unknown services on non-standard ports
   - Generates appropriate XP rewards and notifications for discoveries

2. **Template-Based Content System**
   - Created a template processing system (`template-processor.sh`) for dynamic content generation
   - Implemented service-specific templates for common services (web, database, monitoring)
   - Added unknown service template for handling custom/unexpected services
   - Templates include narrative content, challenge definitions, and documentation

3. **Network Map Integration**
   - Enhanced the network map to visually display discovered services
   - Added rich ASCII visualization for different service types
   - Updated the legend to include detailed service information
   - Added support for unknown/custom services in the visualization

4. **Narrative Integration**
   - Created new quest for service discovery
   - Added journal entry generation based on discovered services
   - Implemented conditional challenge generation based on service combinations
   - Enhanced storytelling by connecting discoveries to The Architect's disappearance

5. **Game Engine Integration**
   - Updated the core engine to detect service discovery commands
   - Added hints for players to guide them to service discovery
   - Created workflow integration to ensure natural gameplay progression

### Usage
To use the enhanced service discovery:

1. Players first need to map the basic network (discover network_gateway and local_network)
2. The game then suggests using service discovery with appropriate hints
3. Players can run `nc-discover-services.sh` to scan for services
4. The network map updates to show discovered services
5. New journal entries and challenges are created based on discoveries

### Technical Details
- Service detection uses `ss`, `netstat`, or `lsof` with fallback mechanisms for compatibility
- Template system uses JSON templates with variable substitution for customization
- Generated content is stored in player's documentation directory
- Service-specific challenges and narratives adapt based on combinations of discoveries

### Future Enhancements
- Add more service templates for additional service types
- Implement network scanning of other hosts beyond localhost
- Create more complex multi-stage challenges based on service combinations
- Add service fingerprinting to detect specific versions and configurations