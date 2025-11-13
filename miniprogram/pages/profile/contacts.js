/**
 * 常用联系人管理页面
 */

const API = require('../../utils/api')
const { showToast, showLoading, hideLoading, showModal } = require('../../utils/toast')

Page({
  data: {
    contacts: [],
    loading: true,
    
    // 编辑弹窗
    showEditModal: false,
    editMode: 'add',  // add / edit
    currentContact: null,
    formData: {
      name: '',
      position: '',
      phone: '',
      email: ''
    }
  },

  onLoad() {
    this.loadContacts()
  },

  /**
   * 加载联系人列表
   */
  async loadContacts() {
    this.setData({ loading: true })
    
    try {
      const response = await API.getContacts()
      console.log('联系人列表:', response)
      
      this.setData({
        contacts: response.items || [],
        loading: false
      })
    } catch (error) {
      console.error('加载联系人失败:', error)
      this.setData({ loading: false })
      showToast('加载失败', 'error')
    }
  },

  /**
   * 显示新增联系人弹窗
   */
  showAddModal() {
    this.setData({
      showEditModal: true,
      editMode: 'add',
      currentContact: null,
      formData: {
        name: '',
        position: '',
        phone: '',
        email: ''
      }
    })
  },

  /**
   * 显示编辑联系人弹窗
   */
  showEditModalForContact(e) {
    const contact = e.currentTarget.dataset.contact
    
    this.setData({
      showEditModal: true,
      editMode: 'edit',
      currentContact: contact,
      formData: {
        name: contact.name,
        position: contact.position || '',
        phone: contact.phone || '',
        email: contact.email || ''
      }
    })
  },

  /**
   * 关闭编辑弹窗
   */
  closeEditModal() {
    this.setData({ showEditModal: false })
  },

  /**
   * 表单输入
   */
  onInput(e) {
    const field = e.currentTarget.dataset.field
    this.setData({
      [`formData.${field}`]: e.detail.value
    })
  },

  /**
   * 保存联系人
   */
  async saveContact() {
    const { editMode, currentContact, formData } = this.data
    
    // 验证
    if (!formData.name.trim()) {
      showToast('请输入姓名', 'none')
      return
    }
    
    showLoading(editMode === 'add' ? '创建中...' : '保存中...')
    
    try {
      if (editMode === 'add') {
        // 创建
        await API.createContact(formData)
        showToast('创建成功', 'success')
      } else {
        // 更新
        await API.updateContact(currentContact.id, formData)
        showToast('保存成功', 'success')
      }
      
      this.closeEditModal()
      this.loadContacts()
    } catch (error) {
      console.error('保存联系人失败:', error)
      showToast('保存失败', 'error')
    } finally {
      hideLoading()
    }
  },

  /**
   * 删除联系人
   */
  async deleteContact(e) {
    const contact = e.currentTarget.dataset.contact
    
    const res = await showModal(
      '确认删除',
      `确定要删除联系人"${contact.name}"吗？`
    )
    
    if (!res.confirm) return
    
    showLoading('删除中...')
    
    try {
      await API.deleteContact(contact.id)
      showToast('删除成功', 'success')
      this.loadContacts()
    } catch (error) {
      console.error('删除联系人失败:', error)
      showToast('删除失败', 'error')
    } finally {
      hideLoading()
    }
  }
})

