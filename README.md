<div align="center">

# NAVI Hobby Project – AI Chat Assistant

</div>

<p align="center">
  <img width="445" height="394" alt="logo" src="https://github.com/user-attachments/assets/05cfa43b-f4cf-4c18-9832-56919e5a7038" />
</p>



## 🚀 Deployment 

**vercel**: [Vercel Deployment Link](https://nextjs-frontend-eight-neon.vercel.app)  

## 🎥 Demo vedio

**loom** [Watch Video Demo](https://www.loom.com/share/d53c4110e321473e9b3495930707da90?sid=a1851f8d-5976-4be4-9d37-171567f4ec95)  


## ✨ Features

- **Interactive Chat UI** with message bubbles and timestamps
- **Animated Typing Indicators** for realistic conversation flow
- **Hobby-themed Background** with floating topic elements
- **Conversation Restart** functionality
- **Responsive Design** works on all devices
- **Smooth Animations** for messages and UI elements
- **Professional Color Scheme** with gradients

## 🛠 Tech Stack

**Frontend**:
- Next.js (React)
- TypeScript
- CSS Animations
- Custom hooks for state management

**Backend**:
- Python (FastAPI/Flask)
- REST API endpoints
- Conversation memory

## 📸 Screenshots

<img width="1678" height="836" alt="Screenshot 2025-07-27 at 9 17 10 PM" src="https://github.com/user-attachments/assets/d891e996-b40d-4321-a6fb-8d11855c97d1" />


## 💬  Prompt for Candidate
"Imagine a user tells you they dislike loud environments and love nature and art. How would your chatbot guide them to suitable hobbies using LangGraph? Explain briefly in your README or a separate design document."

### How the Chatbot Guides Users

**Input:**  
User dislikes loud environments and loves nature/art.

**Process:**  
1. **Detects Interests/Dislikes:**
   - Extracts `"nature"`, `"art"` as interests
   - Flags `"loud environments"` as a dislike

2. **Filters Suggestions:**
   - ✅ Recommends:
     - *Nature:* Birdwatching, gardening
     - *Art:* Painting, pottery
   - ❌ Avoids: Choirs, dance classes

**Sample Conversation Flow:**  
```
Bot: "Try nature sketching—peaceful and creative!"
User: "I'm not good at drawing..."
Bot: "How about nature photography instead?"
```


### Why It Works
- `HOBBY_KNOWLEDGE_BASE` contains quiet/artistic options  
- `SYSTEM_PROMPT` ensures gradual, personalized suggestions  
- No changes needed—already optimized!  

**One-Liner:**  
*"Your bot naturally recommends quiet nature/art hobbies while filtering out loud ones—just as requested!"* 🌿🎨

