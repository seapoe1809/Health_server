#/* DARNA.HI
# * Copyright (c) 2023 Seapoe1809   <https://github.com/seapoe1809>
# * Copyright (c) 2023 pnmeka   <https://github.com/pnmeka>
# * 
# *
# *   This program is free software: you can redistribute it and/or modify
# *   it under the terms of the GNU General Public License as published by
# *   the Free Software Foundation, either version 3 of the License, or
# *   (at your option) any later version.
# *
# *   This program is distributed in the hope that it will be useful,
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *   GNU General Public License for more details.
# *
# *   You should have received a copy of the GNU General Public License
# *   along with this program. If not, see <http://www.gnu.org/licenses/>.
# */

import gradio as gr
import time
import os
from ollama import AsyncClient
import asyncio

model='gemma3:4b'

class HealthMotivator:
    async def get_motivation(self, result):
        print('Result', result)
        messages = [
            {"role": "system", "content": "You are Darnabot, anxiety and cognitive behavioral therapy expert. Provide a brief message given context. No preamble."},
            {"role": "user", "content": f"Given clinical context: {result} give relevant information about anxiety and develop a small exercise using cognitive behavioral technique around acknowledge, identify as intrusive thought, depersonalise as a chemical reaction and finally refocus using breathing and distraction in detail. "},
        ]
        
        try:    
            OLLAMA_HOST = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')
            async for part in await AsyncClient(host=OLLAMA_HOST).chat(model, messages=messages, stream=True):
                yield part['message']['content']
        except Exception as e:
            yield f"Remember to take care of your health. Please see links below! (Error: {str(e)})"
        
                

motivator = HealthMotivator()

async def darnabot_says(result):
    motivation = "Please see a Doctor for advice! "   
    async for chunk in motivator.get_motivation(result):
        motivation += chunk
        yield motivation
        
# Questionnaire
def calculate_gad7_score(q1, q2, q3, q4, q5, q6, q7):
    """
    Calculate GAD-7 score based on responses to 7 questions.
    Each question is scored 0-3 based on frequency of symptoms.
    """
    # Convert responses to scores
    response_values = {
        "Not at all": 0,
        "Several days": 1,
        "More than half the days": 2,
        "Nearly every day": 3
    }
    
    # Calculate total score
    scores = [q1, q2, q3, q4, q5, q6, q7]
    total_score = sum(response_values.get(score, 0) for score in scores)
    
    # Determine severity level
    if total_score <= 4:
        severity = "Minimal anxiety"
    elif total_score <= 9:
        severity = "Mild anxiety"
    elif total_score <= 14:
        severity = "Moderate anxiety"
    else:
        severity = "Severe anxiety that interferes with daily functioning"
    
    return f"Total GAD-7 Score for generalized anxiety: {total_score}\nSeverity: {severity}"

##Exercise
# Function to display exercise details
def display_exercise(exercise):
    exercises = {
        "Step 1: Get present": {
            "text": "**STEPS: Get Present**:\n1. Choose a comfortable and quiet spot. \n2. Follow 5-4-3-2-1 Exercise as shown. \n 3. Click Start when ready.",
            "gif": "54321.png"
        },
        "Step 2: Vagal Breath Exercise": {
            "text": "**STEPS: This works by activating your vagal system.**\n1. Choose a comfortable and quiet place to do your exercise. \n2. Lie down. \n3. Inhale deeply.\n4. Exhale AGAINST closed throat gently pushing out your belly for 6–8 seconds for few seconds and let go.\n 4. Repeat. Stop if you feel dizzy. \n5. Click Start when ready.",
            "gif": "boston_breath.webp"
        }
    }
    
    text = exercises[exercise]["text"]
    UPLOADS_DIR = "uploads"
    gif_path = os.path.join(UPLOADS_DIR, exercises[exercise]["gif"])
    return text, gif_path

# Timer function for 30s reverse countdown
def timer(exercise):
    if not exercise:
        return "<div style='font-size: 30px; text-align: center;'>Please select an exercise first!</div>"
   
    for i in range(60, -1, -1):
        time.sleep(1)
        yield f"<div style='font-size: 30px; text-align: center;'>{i} seconds left</div>" if i > 0 else "<div style='font-size: 30px; text-align: center;'>Great Work!</div>"

# Gradio interface
with gr.Blocks(theme='Taithrah/Minimal', css="footer{display:none !important}") as demo:
    gr.Markdown("<div style='text-align: center; display: flex; align-items: center; justify-content: center; height: 100%; color: #FFFFFF; background-color: #4c00b0; font-weight: bold;'>Anxiety-OCD Darnahi Module</div>")
   
    Introduction = f"""Summary: 
    \n* Anxiety is a natural fear response rooted in our biology, once useful for survival but often unnecessary in modern daily life.
    \n* It comes in different forms—like performance or anticipatory anxiety—and should ease once the trigger passes; persistent anxiety may signal a disorder.
    \n* Worry thoughts fuel anxiety, especially when paired with strong emotional reactions; learning to observe thoughts without judgment can help reduce their impact.

 \n**Understanding Anxiety**

---

**Introduction to Anxiety**

Anxiety is a natural part of the human experience—one that nearly everyone encounters at some point in their life. It can range from mild unease before a job interview to intense, overwhelming fear during a panic attack. But to understand anxiety better, it's important to look beyond its modern manifestations and examine its roots in our biology, its different forms, and how our thoughts and emotional responses can influence it.

---

### **Anxiety as a Chemical Reaction and a Type of Fear**

At its core, anxiety is a chemical and physiological reaction in the body. It is closely related to fear, a primitive emotion that evolved to protect us from danger. When early humans lived in jungles and were exposed to constant threats—like predators such as tigers—this fight-or-flight response was essential for survival. The body would release stress hormones like adrenaline and cortisol, speeding up the heart rate, sharpening focus, and priming muscles to either run or fight. In that context, anxiety had a clear and valuable purpose: keeping us alive.

However, in modern life, we rarely face physical threats like predators. The dangers we now perceive are more psychological and abstract: deadlines, social interactions, financial stress, or uncertain futures. Despite the change in the nature of threats, our brains still respond in the same way they did thousands of years ago. This mismatch between old biology and new environments means anxiety is often activated when it's not truly necessary. In everyday life, anxiety usually serves little to no functional purpose. In fact, it can interfere with our ability to think clearly, solve problems, or interact socially, especially when it's persistent or disproportionate.

---

### **Different Types of Anxiety and Its Ebb and Flow**

Anxiety doesn’t always present the same way. It comes in various forms and can ebb and flow depending on a person’s life circumstances, personality, and biological makeup. In many cases, anxiety is tied to a specific trigger. For example, separation anxiety occurs when individuals feel distress about being away from loved ones. Performance anxiety arises before public speaking or an important task. Anticipatory anxiety may set in when someone fears a future event, even if it's days or weeks away.

These types of anxiety are typically short-lived. Once the triggering situation passes—like once a speech is over or a loved one returns—the anxiety should naturally subside. But when anxiety persists even without clear external triggers, or when it interferes with daily functioning, it may point toward something more chronic, like Generalized Anxiety Disorder (GAD). People with GAD often experience excessive worry over a wide range of everyday issues, and the anxiety doesn't go away easily. Understanding the pattern—whether anxiety comes and goes or remains constant—can help determine whether it's a normal reaction or something that might benefit from professional support.

---

### **Worry Thoughts and the Emotional Response Loop**

One of the most common features of anxiety is the presence of worry thoughts. These are repetitive, often irrational thoughts that circle around worst-case scenarios, uncertainties, or personal inadequacies. When someone experiences anxiety frequently, the mind can become sensitized—hyper-aware of potential dangers or discomforts. This leads to a flood of worry thoughts that are not necessarily based in reality but feel very real to the person experiencing them.

It's important to understand that the human brain generates up to 50,000 thoughts a day. Most of these are fleeting, neutral, or irrelevant. However, when someone is anxious, they may latch onto certain thoughts and interpret them as meaningful or dangerous. What turns an ordinary thought into a source of suffering is not the thought itself, but the emotional response that follows. For example, thinking "What if I embarrass myself?" might trigger feelings of shame, fear, or panic. This emotional reaction amplifies the thought, making it feel more urgent and real, which then worsens the anxiety. This becomes a loop—anxious thoughts produce emotional reactions, which increase anxiety, which in turn leads to more anxious thoughts.

Recognizing that thoughts are not always reflective of reality or personal worth can be a powerful first step toward managing anxiety. Just because a thought enters your mind doesn’t mean it’s true or deserves your full attention. Learning to observe thoughts without judgment—and to reduce the emotional weight we attach to them—is central to many therapeutic approaches for anxiety, such as cognitive-behavioral therapy (CBT) and mindfulness practices.

---

### **Conclusion**

Anxiety is a deeply rooted survival mechanism, once essential for avoiding real danger, but now often triggered by modern stressors where no immediate threat exists. It manifests in many ways and is commonly tied to specific situations, although it can become chronic if it doesn’t subside after the trigger disappears. The mental chatter of worry thoughts, particularly when accompanied by strong emotional reactions, plays a major role in fueling ongoing anxiety. Understanding anxiety for what it is—a natural but often misdirected biological process—can be the first step toward gaining control over it and reducing its impact on daily life.

---



***Take the self assessment test to assess your risk!***
"""
    
    worry_thoughts = """Summary: 
    \n* Generalized anxiety involves persistent, excessive fears that interfere with daily life, often without a clear trigger.    
   \n* Worry thoughts are intensified when anxiety sensitizes the mind, and emotional reactions like guilt can turn harmless thoughts into obsessive loops.
   \n* Obsessions and compulsions may follow, often driven by reassurance-seeking, but long-term relief comes from reducing baseline anxiety through CBT and ERP. Medications are also an option inn addition.



---

### **Generalized Anxiety – Persistent Fears Interfering with Daily Life**

Generalized Anxiety Disorder (GAD) is characterized by persistent, excessive worry about various aspects of everyday life—such as work, health, relationships, or routine responsibilities. Unlike situational anxiety, which is triggered by specific events and fades afterward, generalized anxiety lingers and spreads across multiple domains. People with GAD often find it difficult to control their worry, even when they recognize it as disproportionate or irrational.

This chronic state of fear and anticipation can significantly interfere with day-to-day functioning. It may lead to trouble concentrating, fatigue, restlessness, irritability, muscle tension, and sleep disturbances. What distinguishes GAD from normal worry is not just the intensity but the *persistence*—the anxiety remains even when there's no immediate reason to feel anxious. Over time, this persistent tension creates a baseline of heightened alertness in the nervous system, making the individual more sensitive to future stressors and worry thoughts.

---

### **Worries: When Anxiety Sensitizes the Mind**

Worries are a hallmark symptom of anxiety and can become more frequent and intense when the mind is in a sensitized state. This often happens when anxiety has been present for a long time, elevating the brain's threat-detection system. In such a state, even minor or harmless thoughts can trigger an emotional response—like fear, guilt, or panic. The problem isn't the thought itself, but the emotional weight it carries.

The average person has around 50,000 thoughts per day. Many are random, fleeting, or even bizarre. Having a strange or unsettling thought—like an intrusive idea or a sudden fear—doesn’t reflect on your character or intentions. But when anxiety is heightened, people often misinterpret these thoughts as meaningful or dangerous, which then triggers guilt or shame. For example, someone might think, *“What if I lose control and hurt someone?”* and immediately feel disturbed, fearing they’re a bad person. This response worsens the anxiety and makes the thought feel more real.

Over time, overanalyzing these thoughts—also called **rumination**—can escalate the cycle. The more someone tries to analyze, disprove, or avoid the thought, the more power it gains. If this pattern continues unchecked, it can evolve into obsessive thinking and even compulsive behaviors, especially when the mind starts demanding reassurance or certainty to relieve the emotional distress.

---

### **Obsessions and Compulsions Can Occur with Significant Anxiety**

Obsessions are intrusive, distressing thoughts or images that repeatedly enter a person's mind, while compulsions are the actions or mental rituals performed to neutralize the anxiety those thoughts cause. This obsessive-compulsive cycle is often fueled by high baseline anxiety. For instance, someone might obsess over whether they offended a friend, leading them to seek constant reassurance by re-reading messages or repeatedly asking others for validation.

While reassurance may seem helpful in the moment, it often makes things worse in the long term. Why? Because it reinforces the idea that the worry is valid and must be solved immediately. The brain learns that anxiety is intolerable unless relieved by reassurance or ritual, which strengthens the anxiety-reassurance loop. Over time, this loop becomes automatic and harder to break.

Even compulsions that seem minor—like double-checking locks or repeating phrases mentally—can grow into time-consuming rituals if they’re continually used as a coping mechanism for anxiety. That's why treatment must be cautious with reassurance, instead promoting toleration of discomfort and uncertainty.

---

### **Imagining the Relationship: The Bubble Analogy**

To understand how anxiety feeds into worries, obsessions, and compulsions, imagine a toy you may have played with as a child—a bubble maker. It typically has a fan and a rotating soapy frame. The faster the fan spins, the more bubbles it produces, and the bigger they get.

In this analogy, **the fan represents your anxiety baseline**, and the **bubbles represent worry thoughts**. When the fan is on low (low anxiety), a few small bubbles float out—minor worries that come and go. But turn the fan up (heightened anxiety), and the machine pumps out a flood of bubbles—worry thoughts come faster, feel bigger, and are harder to ignore. Some may even burst in your face—just like intense emotional reactions triggered by specific thoughts.

This simple image captures a key insight: **it's not just about managing individual thoughts or worries, but about turning down the base setting of anxiety itself**. Gold standard treatments like **Cognitive Behavioral Therapy (CBT)** and **Exposure and Response Prevention (ERP)** target both components—helping individuals reframe distorted thoughts *and* reduce the underlying anxiety that fuels the entire process. ERP, for example, exposes individuals to feared thoughts or situations without allowing the typical compulsion or reassurance that follows. Over time, this builds tolerance to discomfort and teaches the brain that the anxiety will pass without needing to act on it.

---
### **Panic Attacks – Sudden Surges of Intense Anxiety**

Panic attacks are sudden, intense episodes of fear that can feel overwhelming and terrifying. They often occur without warning and may include physical symptoms such as a racing heart, shortness of breath, chest pain, dizziness, sweating, or a feeling of losing control. Many people experiencing a panic attack fear they are having a heart attack or going crazy, even though the symptoms are **not life-threatening**. Panic attacks are closely linked to anxiety disorders and can arise when the body’s fight-or-flight system becomes hyperactive. While the episodes are typically short-lived, the fear of having another attack can lead to avoidance behaviors and further anxiety. Understanding that these attacks are a result of heightened physiological arousal—not true danger—is key to managing and reducing them over time, often through techniques taught in CBT and exposure-based therapies.

---
### **Conclusion**

Generalized anxiety, worry thoughts, and obsessions/compulsions are all connected by the common thread of heightened emotional and physiological response. When anxiety sensitizes the mind, even ordinary thoughts can spiral into emotional distress, leading to a vicious cycle of rumination, guilt, and reassurance-seeking. Understanding the mechanics of this cycle—and visualizing how a high anxiety "setting" amplifies everything—can help demystify the experience. Effective treatment aims not only to question and reframe thoughts but to reduce the overall anxiety threshold, making the mind more resilient and less reactive in the long run.




"""
    
    Diagnosis_treatment = """Summary: 
    \n* Breathing, grounding, and reframing help manage anxiety in the moment by calming the body and shifting perspective.

\n* The IARR method teaches you to observe, detach from, and reframe intrusive or anxious thoughts.

\n* Exercise, journaling, and physical release support long-term anxiety management by regulating mood and offering emotional relief.

\n* Managing anxiety isn’t about eliminating it—it’s about understanding and redirecting it in healthier, more empowering ways.


---

## **Managing Anxiety: Practical Tools and Techniques**

Anxiety is a complex and often overwhelming experience, but it can be managed effectively with consistent techniques that help regulate the nervous system and shift our mental and emotional focus. Whether your anxiety stems from generalized worry, intrusive thoughts, or panic symptoms, using a mix of physical, cognitive, and behavioral strategies can reduce its intensity and restore a sense of control.

---

### **Breathing Techniques: Box Breaths and Vagal Breaths**

Breathing is one of the fastest ways to calm the nervous system. Two simple but powerful techniques are **Box Breathing** and **Vagal Breathing**.

**Box Breathing** involves inhaling for 4 seconds, holding for 4 seconds, exhaling for 4 seconds, and holding again for 4 seconds—like tracing the sides of a square. This technique helps regulate breathing and signals the body to shift from fight-or-flight mode to rest-and-digest.

**Vagal Breathing** stimulates the vagus nerve, which plays a key role in calming the body. To practice, take a slow breath in through your nose for 4 seconds, then exhale against closed throat gently pushing out your belly for 6–8 seconds, followed by a whoosh exhale. This longer exhale helps activate the parasympathetic nervous system, reducing heart rate and anxiety.

Practicing either of these for few minutes a day can have a noticeable impact on anxiety levels especialy before sleeping.

---

### **Grounding and Reframing Techniques**

When anxiety strikes, grounding and reframing techniques can help bring you back to the present and reshape the meaning you assign to your thoughts and feelings.

**Grounding** involves reconnecting with your senses. For instance, attending a concert, meeting a friend, or even going for a walk can shift your focus from internal worries to external experience. A simple method is the “5-4-3-2-1” technique—naming 5 things you see, 4 you can touch, 3 you hear, 2 you smell, and 1 you taste.

**Reframing** is about shifting perspective. Instead of thinking, “I’ll fail if I go out,” reframe it as, “I might be anxious, but it could still be fun or meaningful.” Seeking out “one good thing” in a situation—like enjoying the music at a concert or connecting with a stranger—can change how you perceive and remember the experience, reducing future anxiety.

---

### **The IARR Method: Identify, Attribute, Refocus, Revalue**

The **IARR method** is especially helpful for managing intrusive thoughts and worry spirals, particularly in anxiety and OCD-related conditions. Here's how it works:

* **Identify (or Relabel):** Recognize the thought for what it is—a symptom of anxiety or OCD. Say to yourself, “This is just an anxious thought,” instead of taking it at face value.
* **Attribute (or Reattribute):** Understand that this thought arises from a misfiring in the brain—not because it's true or meaningful. This insight reduces the weight you give the thought.
* **Refocus:** Engage in a constructive activity, like exercising, reading, or cooking. Shifting focus helps break the habit of ruminating and trains the brain to respond differently.
* **Revalue:** With time, you’ll start seeing these thoughts as distractions rather than dangers. They lose their emotional charge, and you can prioritize what matters most to you.

This method builds resilience by breaking the cycle of fear, reaction, and reinforcement.

---

### **Journaling: Tracking Symptoms and Building a Flight Plan**

Journaling is a simple yet effective way to externalize your inner experience. By regularly writing down your symptoms, triggers, and what strategies you used to cope, you begin to notice patterns—and progress. Keeping a “flight plan” (a short list of coping tools that work for you) gives you a go-to reference when anxiety hits.

Writing also provides emotional release and helps process difficult thoughts. It can turn chaotic inner dialogue into clear, manageable steps, giving you a sense of agency over your anxiety.

---

### **Exercise: Natural Dopamine and Mood Boost**

Exercise is a proven anxiety reducer. Even just 15–20 minutes of brisk walking, light jogging, or yoga can elevate dopamine and serotonin levels—brain chemicals associated with mood regulation. Consistency matters more than intensity. Doing short workouts once or twice a day, especially in fresh air, can ground your body and release built-up stress.

Exercise also shifts your focus away from overthinking and provides a sense of accomplishment, reinforcing your ability to cope.

---

### **Release: Mimicking Fight with Controlled Action**

Anxiety activates the fight-or-flight response. When the "fight" energy builds up but has no outlet, it can make us feel restless, irritable, or panicked. One simple strategy is **controlled release**—punching a sandbag or pillow for a few minutes, shouting into a cushion, or doing vigorous movements like jumping jacks. These actions mimic the "fight" response and give the body a chance to discharge excess adrenaline.

It’s not about aggression—it's about providing your nervous system with a safe outlet to reset and calm down.

---

### **Summary **
Managing anxiety isn’t about eliminating it—it’s about understanding and redirecting it in healthier, more empowering ways.




**Important Note**
\nPlease see a doctor for treatment advice. The intent is only informational in this app!
"""
    
    with gr.Tab("GET STARTED STEPWISE"):
        gr.Markdown("# STEP1: AI ASSESSMENT: DARNABOT")
        with gr.Accordion(label="QUICK ASSESSMENT: Do I have Generalized Anxiety?📋", open=False):
         
            gr.Markdown("# Anxiety (GAD-7) Assessment")
            gr.Markdown("Over the last 2 weeks, how often have you been bothered by the following problems?")
    
            response_choices = ["Not at all", "Several days", "More than half the days", "Nearly every day"]
    
            with gr.Column():
                q1 = gr.Radio(choices=response_choices, label="1. Feeling nervous, anxious, or on edge", value="Not at all")
                q2 = gr.Radio(choices=response_choices, label="2. Not being able to stop or control worrying", value="Not at all")
                q3 = gr.Radio(choices=response_choices, label="3. Worrying too much about different things", value="Not at all")
                q4 = gr.Radio(choices=response_choices, label="4. Trouble relaxing", value="Not at all")
                q5 = gr.Radio(choices=response_choices, label="5. Being so restless that it is hard to sit still", value="Not at all")
                q6 = gr.Radio(choices=response_choices, label="6. Becoming easily annoyed or irritable", value="Not at all")
                q7 = gr.Radio(choices=response_choices, label="7. Feeling afraid, as if something awful might happen", value="Not at all")
        
                check_btn = gr.Button("Calculate GAD-7 Score")
                result = gr.Textbox(label="Summary by Darnabot:", lines=2)
                outputd = gr.Markdown(label="Darnabot:")
    
            check_btn.click(fn=calculate_gad7_score, inputs=[q1, q2, q3, q4, q5, q6, q7], outputs=result).then(fn=darnabot_says, inputs=result, outputs=outputd)
                

                #check_btn.click(fn=check_strep, inputs=[high_risk, age, exudate, nodes, fever, cough], outputs=result).then(fn=darnabot_says, inputs=result, outputs=outputd)

    gr.Markdown("# STEP 2: UNDERSTAND ANXIETY")
    gr.Markdown("Click on any chapter to expand it.")
        
    with gr.Accordion("Chapter 1: Introduction 👈", open=False) as chapter1:
            gr.Markdown("## Chapter 1 Introduction")
            gr.Markdown(Introduction)
            with gr.Group():
                gr.Image("uploads/anxiety_normal.jpeg", show_label=True)
                gr.Markdown("**Figure 1:** Anxiety a type of fear- Anxiety is a natural fear response rooted in our biology, once useful for survival but often unnecessary in modern daily life.")
                gr.Image("uploads/anxiety.jpg", show_label=False)
                gr.Markdown("**Figure 2:** Not normal anxiety- when anxiety persists even without clear external triggers, or when it interferes with daily functioning, it may point toward something more chronic, like Generalized Anxiety Disorder (GAD).")
        
    with gr.Accordion("Chapter 2: Understanding Generalized anxiety /Obsessions & Compulsions 👈", open=False) as chapter2:
            gr.Markdown("## Chapter 2 Anxiety Complications ")
            gr.Markdown(worry_thoughts)
            with gr.Group():
                gr.Image("uploads/4_step.jpeg", show_label=True)
                gr.Markdown("**Figure 1:** The Identify, Attribute, Refocus, Revalue (IARR) method, is a technique introduced by Dr. Jeffrey Schwartz is helpful in dealing with anxiety complicated by worry thoughts and obsessions. ")
        
    with gr.Accordion("Chapter 3: Build skillsets 👈", open=False) as chapter3:
            gr.Markdown("## Chapter 3 Untangling Anxiety")
            gr.Markdown(Diagnosis_treatment)
            
    
           
    gr.Markdown("# STEP 3: SOS")
    with gr.Accordion("Chapter4: Anxiety Attack? 2 Step SOS 👈", open=False) as chapter4:
            gr.Markdown("## Every thing is OK! You got this. Start with Dropdown to begin.")
            with gr.Row():
                    with gr.Column():
                        dropdown = gr.Dropdown(
                        choices=["Step 1: Get present", "Step 2: Vagal Breath Exercise"], 
                        value=None, 
                        interactive=True, 
                        label="Stress/Anxiety Exercises (1 min)"
            
                    )
                        text_output = gr.Markdown()
            
                    with gr.Column():
                        image_output = gr.Image(type="filepath", label="Exercise:")
                        timer_output = gr.HTML(label="60s Reverse Timer")
    
                        submit_button = gr.Button("Start", interactive=False)
        
            def enable_submit(exercise):
                    if exercise:
                        return gr.update(interactive=True)
    
            # Update text and display the exercise GIF when the dropdown changes
            dropdown.change(display_exercise, inputs=dropdown, outputs=[text_output, image_output])
            dropdown.change(enable_submit, inputs=dropdown, outputs=submit_button)
    
            # When the button is clicked, start the 30-second timer and display the countdown
            submit_button.click(timer, inputs=dropdown, outputs=timer_output)
            
    gr.Markdown("# MORE LINKS")
    gr.HTML("""
        <a href="https://www.actmindfully.com.au/free-stuff/" target="_blank">Daily Free Audio and Video Resources 🔗 </a>
    """)
    gr.HTML("""
        <a href="https://newsroom.clevelandclinic.org/2024/03/15/benefits-of-fermented-food-for-your-mental-health" target="_blank">Daily Fermented foods for Anxiety- Yogurt, Kimchi and Indian Crepe 🔗 </a>
    """)
    gr.HTML("""
        <a href="https://www.health.harvard.edu/mind-and-mood/omega-3s-for-anxiety" target="_blank">Daily Omega-3 supplements for Anxiety 🔗 </a>
    """)
    gr.HTML("""
        <a href="https://www.health.harvard.edu/blog/can-exercise-help-treat-anxiety-2019102418096" target="_blank">15 Minutes of Vigorous Exercise a Day! 🔗 </a>
    """)
    
    

if __name__ == "__main__":
    demo.launch(server_name='0.0.0.0', server_port=3028, pwa=True, share=False)


"""""

"""""
