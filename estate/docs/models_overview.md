# Estate Module – 模型与视图总览（按你当前代码生成）

> 目的：把目前模块里“有哪些模型/字段/关系/逻辑/视图/菜单”整理成一张可读地图，方便你后续做 Chapter 9 按钮动作和任何调试。
> 
> 说明：此文件只给人看，不会被 Odoo 加载。

---

## 1. 模块总览

### 1.1 主要模型
- `estate.property`：房源（核心业务对象）
- `estate.property.offer`：报价（房源的一对多子对象）
- `estate.property.type`：房源类型（配置/字典表）
- `estate.property.tag`：房源标签（配置/字典表）

### 1.2 主要关系图（只列你自定义的关系字段）
- `estate.property.property_type_id` → `estate.property.type` (Many2one)
- `estate.property.buyer_id` → `res.partner` (Many2one)
- `estate.property.salesperson_id` → `res.users` (Many2one)
- `estate.property.tag_ids` ↔ `estate.property.tag` (Many2many)
- `estate.property.offer_ids` → `estate.property.offer` (One2many)
- `estate.property.offer.property_id` → `estate.property` (Many2one)
- `estate.property.offer.partner_id` → `res.partner` (Many2one)

---

## 2. Model: `estate.property`（房源）

**文件**：`models/estate_property.py`

### 2.1 字段分组（按业务理解分）

#### A) 基本信息
- `title` (Char, **required**)
- `description` (Text)
- `postcode` (Char)
- `date_availability` (Date)
  - `copy=False`
  - 默认值：今天 + 3 个月（`fields.Date.add(fields.Date.today(), months=3)`）

#### B) 价格信息
- `expected_price` (Float, **required**)
- `selling_price` (Float)
  - `readonly=True`, `copy=False`

#### C) 房屋属性
- `bedrooms` (Integer, default=2)
- `living_area` (Integer)（label: "Living Area (sqm)"）
- `facades` (Integer)
- `garage` (Boolean)
- `garden` (Boolean)
- `garden_area` (Integer)
- `garden_orientation` (Selection: `north/south/east/west`)

#### D) 流程状态
- `state` (Selection, **required**, `copy=False`, default=`new`)
  - 可选值：`new / offer_received / offer_accepted / sold / cancelled`
- `active` (Boolean, default=True)

#### E) 关系字段（跨模型）
- `property_type_id` (Many2one → `estate.property.type`)
- `buyer_id` (Many2one → `res.partner`, `copy=False`)
- `salesperson_id` (Many2one → `res.users`, default=`env.user`)
- `tag_ids` (Many2many → `estate.property.tag`)
- `offer_ids` (One2many → `estate.property.offer`, inverse=`property_id`)

#### F) 计算字段 / 派生字段
- `total_area` (Float, compute=`_compute_total_area`)
  - depends：`living_area`, `garden_area`
  - 逻辑：`(living_area or 0) + (garden_area or 0)`
- `best_price` (Float, compute=`_compute_best_price`)
  - depends：`offer_ids.price`
  - 逻辑：取所有 offers 的 `price` 最大值；没有报价则为 0

#### G) validity / deadline（你当前也在 property 上定义了一套）
> 注：教程原版通常把 validity/deadline 放在 `offer` 上；你这里在 `property` 上也定义了一套（不一定错，但容易让自己混乱）。

- `validity` (Integer, default=7)
- `date_deadline` (Date, compute=`_compute_date_deadline`, inverse=`_inverse_date_deadline`)

### 2.2 自动逻辑（compute / inverse / onchange）

#### `_compute_total_area`
- `@api.depends('living_area', 'garden_area')`
- 目的：自动更新 `total_area`

#### `_compute_best_price`
- `@api.depends('offer_ids.price')`
- 用法亮点：`mapped('price')` 把 recordset 映射成值列表

#### `_compute_date_deadline` / `_inverse_date_deadline`
- 当前实现：用 `create_date + validity(days)` 计算 deadline
- 当前 depends：`@api.depends('date_availability', 'validity')`
  - **注意点**：depends 写了 `date_availability`，但方法内部实际没用它，而是用 `create_date`。

#### `_onchange_garden`
- `@api.onchange('garden')`
- 逻辑：
  - 勾选 `garden`：`garden_area=10`, `garden_orientation='north'`
  - 取消 `garden`：`garden_area=0`, `garden_orientation=False`

### 2.3 业务规则 / 约束（当前实现）
- 你写了：`_check_expected_price = models.Constraint(...)`
- **常见/标准写法**：使用 `_sql_constraints = [(name, sql, message), ...]`。
- 如果你的 Odoo 版本没有 `models.Constraint` 这个写法，这里会导致模块加载时报错。

### 2.4 Chapter 9 需要新增的按钮动作（TODO）
> 你当前 `estate.property` 还没有 action 方法。

- `action_cancel()`
  - 规则：`state == 'sold'` 时禁止取消（抛 `UserError`）
  - 成功：`state = 'cancelled'`
- `action_sold()`
  - 规则：`state == 'cancelled'` 时禁止售出（抛 `UserError`）
  - 成功：`state = 'sold'`

---

## 3. Model: `estate.property.offer`（报价）

**文件**：`models/estate_property_offer.py`

### 3.1 字段分组

#### A) 核心字段
- `price` (Float, **required**)
- `status` (Selection, `copy=False`)
  - 可选值：`accepted / refused`
  - 备注：目前没有 default，新建 offer 时 `status` 为 False

#### B) 关系字段
- `partner_id` (Many2one → `res.partner`, **required**)
- `property_id` (Many2one → `estate.property`, **required**)

#### C) validity / deadline
- `validity` (Integer, default=7)
- `date_deadline` (Date, compute=`_compute_date_deadline`, inverse=`_inverse_date_deadline`)
  - depends：`create_date`, `validity`

### 3.2 自动逻辑（compute / inverse）

#### `_compute_date_deadline`
- `@api.depends('create_date', 'validity')`
- 逻辑：`date_deadline = create_date + validity(days)`

#### `_inverse_date_deadline`
- 逻辑：把 `date_deadline - create_date` 的天数写回 `validity`

### 3.3 Chapter 9 需要新增的按钮动作（TODO）

- `action_accept()`
  - 把当前 offer 标记为 `accepted`
  - 并联动更新对应 property：
    - `buyer_id = partner_id`
    - `selling_price = price`
    - `state = 'offer_accepted'`（或按你的流程设计）
  - 规则：同一 property 只能接受一个 offer
    - 做法：检查 `property_id.offer_ids` 里是否已有 `status == 'accepted'`

- `action_refuse()`
  - 把当前 offer 标记为 `refused`

---

## 4. Model: `estate.property.type`（房源类型）

**文件**：`models/estate_property_type.py`

- `name` (Char, **required**)

---

## 5. Model: `estate.property.tag`（房源标签）

**文件**：`models/estate_property_tag.py`

- `name` (Char, **required**)

---

## 6. 视图（Views）与菜单（Menus）

### 6.1 `estate.property` 视图：`views/estate_property_views.xml`

#### Action
- `estate_property_action`
  - `res_model = estate.property`
  - `view_mode = list,form`

#### List View：`estate_property_view_list`
- 字段：
  - `title, postcode, bedrooms, living_area, expected_price, selling_price, date_availability, state, property_type_id`
  - `tag_ids` 使用 `many2many_tags` 小标签样式

#### Form View：`estate_property_view_form`
- `h1`：显示 `title`
- 顶部：`tag_ids` 以 tags 形式展示
- 中部 group：
  - 左：property_type_id / postcode / date_availability
  - 右：expected_price / best_price / selling_price
- Notebook：
  - `description` 页：description + 房屋属性字段 + total_area
  - `Offers` 页：内嵌 `offer_ids` 的 list（`editable="bottom"`）
    - 字段：price, status, partner_id, validity, date_deadline
  - `Other Info` 页：buyer_id, salesperson_id

#### Search View：`estate_property_view_search`
- 可搜索字段：title, postcode, expected_price, bedrooms, living_area, facades, property_type_id
- Filter：Available（state 为 `new` 或 `offer_received`）
- Group By：postcode

> Chapter 9 视图改动提示：你需要在 property form 的 `<form>` 里加 `<header>`，放 Cancel/Sold 按钮与 state 的 statusbar。

### 6.2 `estate.property.offer` 视图：`views/estate_property_offer_views.xml`

- List View：price, status, partner_id, validity, date_deadline, property_id
- Form View：price, status, partner_id, validity, date_deadline

> 注意：你在 property form 的 Offers 页用的是“内嵌 list”，它不会自动复用这里的 list view。
> 
> 所以如果你把 Accept/Refuse 按钮加在 `estate_property_offer_views.xml` 的 list 里，**property form 的内嵌 offers 表不会出现按钮**。
> 
> 两种可选方案：
> 1) 直接在 property form 的内嵌 `<list>` 里加按钮（最省事）
> 2) property form 里只写 `<field name="offer_ids"/>`，让 Odoo 复用 offer 的 tree view（更干净）

### 6.3 Type/Tag 视图
- `estate.property.type`：list/form/search（`views/estate_property_type_views.xml`）
- `estate.property.tag`：list/form（`views/estate_property_tag_views.xml`）

### 6.4 菜单：`views/estate_menus.xml`
- Root：Real Estate
  - Properties
    - Properties（action: `estate_property_action`）
  - Settings
    - Property Types（action: `estate_property_type_action`）
    - Property Tags（action: `estate_property_tag_action`）

---

## 7. 快速检查清单（你现在就能用来排雷）

- [ ] `estate.property` 的 expected_price 约束是否应改为 `_sql_constraints`
- [ ] `estate.property.date_deadline` 的 depends 与实际逻辑是否一致（现在 depends 写 date_availability，但实现用 create_date）
- [ ] Offer 的 `status` 是否需要更清晰的初始状态（例如加 `new` 或设置 default）
- [ ] Chapter 9：
  - [ ] property form header：Cancel/Sold + statusbar
  - [ ] offer accept/refuse：按钮放在“内嵌 list”还是“复用 tree view”二选一并统一

