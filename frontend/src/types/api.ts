export interface UserProfile {
  phone: string
  nickname: string
  real_name: string
  school: string
  grade: string
  role: string
  avatar_url: string
  is_real_name_auth: boolean
}

export interface CheckInRecord {
  id: number
  day: number
  date: string
  study_duration: number
  entertainment_duration: number
  online_activities: string
  mood: string
  self_rating: number
  created_at: string
}

export interface QuizQuestion {
  id: number
  q_type: 'true_false' | 'choice'
  day: number
  question: string
  option_a: string
  option_b: string
  option_c: string
  option_d: string
  answer: string
  explanation: string
}

export interface Message {
  id: number
  user_name: string
  content: string
  created_at: string
  replies: Reply[]
  likes: number
}

export interface Reply {
  id: number
  user_name: string
  content: string
  created_at: string
}

export interface Notification {
  id: number
  content: string
  n_type: string
  created_at: string
  is_read: boolean
}

export interface PageResponse<T> {
  results: T[]
  total: number
  page: number
  page_size: number
  has_more: boolean
  unread_count?: number
}
