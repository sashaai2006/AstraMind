# LangGraph Migration: Зачем и как

## 🤔 Зачем своя реализация? (Текущая ситуация)

**Текущая реализация** (`backend/core/orchestrator.py`):
- ✅ Простой DAG runner (~200 строк)
- ✅ Параллельные группы через `asyncio.gather()`
- ✅ Базовый stop/cancel механизм
- ✅ WebSocket интеграция

**Проблемы**:
- ❌ **Нет checkpoint persistence** - при перезапуске сервера теряется прогресс
- ❌ **Нет визуализации графа** - сложно отлаживать сложные workflows
- ❌ **Нет встроенного retry** - нужно писать вручную
- ❌ **Нет state management** - состояние размазано по переменным
- ❌ **Нет human-in-the-loop** - сложно добавить эскалацию
- ❌ **Нет conditional routing** - сложно делать динамические ветвления

---

## 🚀 Преимущества LangGraph

### 1. **Checkpoint Persistence** (Критично!)
```python
# LangGraph автоматически сохраняет состояние после каждого шага
# При перезапуске можно восстановить с любого checkpoint
from langgraph.checkpoint.sqlite import SqliteSaver

checkpointer = SqliteSaver.from_conn_string("checkpoints.db")
graph = graph.compile(checkpointer=checkpointer)
```

**Наша текущая проблема**: Если сервер упадёт на шаге 5 из 8, нужно начинать с начала.

### 2. **Визуализация графа**
```python
# LangGraph автоматически генерирует визуализацию
graph.get_graph().draw_mermaid_png(output_file_path="graph.png")
```

**Польза**: Легко понять flow, отладить сложные сценарии, показать пользователю.

### 3. **Встроенный Retry и Error Handling**
```python
from langgraph.errors import GraphRecursionError

# Автоматический retry с экспоненциальной задержкой
# Эскалация к human supervisor при критических ошибках
```

**Наша текущая проблема**: Нужно вручную писать retry логику для каждого агента.

### 4. **State Management**
```python
from typing import TypedDict

class ProjectState(TypedDict):
    project_id: str
    title: str
    description: str
    plan: List[Dict]
    artifacts: List[str]
    status: str
    # LangGraph автоматически управляет этим состоянием
```

**Наша текущая проблема**: Состояние размазано по `context` dict, сложно отслеживать изменения.

### 5. **Human-in-the-Loop**
```python
from langgraph.prebuilt import interrupt_before

# Легко добавить точки остановки для human approval
graph = graph.add_node("human_review", human_review_node)
graph = graph.add_edge("human_review", "continue")
```

**Наша текущая проблема**: Сложно добавить эскалацию к человеку при ошибках.

### 6. **Conditional Routing**
```python
def should_retry(state: ProjectState) -> str:
    if state["retry_count"] < 2:
        return "retry"
    return "escalate_to_human"

graph.add_conditional_edges(
    "developer",
    should_retry,
    {
        "retry": "developer",
        "escalate_to_human": "human_supervisor"
    }
)
```

**Наша текущая проблема**: Нужно писать if/else вручную для каждого случая.

---

## 📊 Сравнение: Custom vs LangGraph

| Функция | Custom (сейчас) | LangGraph |
|---------|----------------|-----------|
| **Checkpoint persistence** | ❌ Нет | ✅ Встроено |
| **Визуализация** | ❌ Нет | ✅ Автоматическая |
| **Retry logic** | ⚠️ Ручная | ✅ Встроено |
| **State management** | ⚠️ Dict-based | ✅ TypedDict + версионирование |
| **Human-in-the-loop** | ❌ Сложно | ✅ Просто |
| **Conditional routing** | ⚠️ If/else | ✅ Декларативно |
| **Отладка** | ⚠️ Логи | ✅ Визуализация + трейсинг |
| **Масштабирование** | ❌ Single instance | ✅ Distributed support |
| **Код** | ~200 строк | ~100 строк (более читаемо) |

---

## 🎯 План миграции на LangGraph

### **Phase 1: Подготовка** (1-2 дня)
1. Установить зависимости:
   ```bash
   pip install langgraph langgraph-checkpoint-sqlite
   ```
2. Создать `ProjectState` TypedDict
3. Определить граф узлов (CEO → Developer → Tester → ...)

### **Phase 2: Миграция узлов** (2-3 дня)
1. Переписать каждый агент как LangGraph node:
   ```python
   async def ceo_node(state: ProjectState) -> ProjectState:
       plan = await ceo_agent.plan(state["description"], state["target"])
       return {"plan": plan}
   ```
2. Сохранить существующую логику агентов (только обёртка)

### **Phase 3: Граф и checkpointing** (1-2 дня)
1. Построить граф:
   ```python
   from langgraph.graph import StateGraph
   
   workflow = StateGraph(ProjectState)
   workflow.add_node("ceo", ceo_node)
   workflow.add_node("developer", developer_node)
   workflow.add_node("tester", tester_node)
   workflow.add_edge("ceo", "developer")
   workflow.add_conditional_edges("developer", should_test)
   ```
2. Добавить checkpoint persistence
3. Интегрировать с WebSocket (broadcast событий)

### **Phase 4: Продвинутые фичи** (2-3 дня)
1. Добавить retry с экспоненциальной задержкой
2. Добавить human-in-the-loop для критических ошибок
3. Добавить conditional routing (например, skip tests если нет изменений)
4. Добавить визуализацию графа в UI

---

## 💡 Рекомендация

**✅ СТОИТ мигрировать на LangGraph**, потому что:

1. **Checkpoint persistence** - критично для продакшена (не терять прогресс)
2. **Меньше кода** - LangGraph делает много работы за нас
3. **Лучшая отладка** - визуализация графа помогает найти проблемы
4. **Готовые паттерны** - retry, human-in-the-loop уже реализованы
5. **Масштабируемость** - LangGraph поддерживает distributed execution

**⏱️ Время миграции**: ~1 неделя (с тестированием)

**Риски**: Минимальные - можно мигрировать постепенно, сохранив старый код как fallback.

---

## 🚦 Альтернатива: AutoGen

**AutoGen** тоже хороший вариант, но:
- ✅ Лучше для multi-agent conversations (чат между агентами)
- ❌ Сложнее для DAG workflows (наш случай)
- ❌ Меньше встроенных фич (checkpoint, retry)

**Вывод**: LangGraph лучше подходит для нашего use case (DAG execution с checkpointing).

---

## 📝 Пример миграции

### До (Custom):
```python
async def _run_project(self, project_id, title, description, target, stop_event):
    plan = await self._ceo.plan(description, target)
    for group_id, steps in self._group_steps(plan):
        await asyncio.gather(*[self._run_step(step, context, stop_event) for step in steps])
    # Нет checkpoint - если упадёт здесь, всё потеряно
```

### После (LangGraph):
```python
from langgraph.graph import StateGraph
from langgraph.checkpoint.sqlite import SqliteSaver

workflow = StateGraph(ProjectState)
workflow.add_node("ceo", ceo_node)
workflow.add_node("developer", developer_node)
workflow.add_node("tester", tester_node)
workflow.set_entry_point("ceo")
workflow.add_edge("ceo", "developer")
workflow.add_conditional_edges("developer", should_test)

checkpointer = SqliteSaver.from_conn_string("checkpoints.db")
app = workflow.compile(checkpointer=checkpointer)

# Автоматический checkpoint после каждого шага
# При перезапуске: app.invoke(state, config={"configurable": {"thread_id": project_id}})
```

---

**Вывод**: Миграция на LangGraph даст нам checkpoint persistence, лучшую отладку и меньше кода. Стоит сделать это в ближайшем спринте.

