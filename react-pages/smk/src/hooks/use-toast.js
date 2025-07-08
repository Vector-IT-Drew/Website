import { toast } from "sonner"

export const useToast = () => {
  return {
    toast: ({ title, description }) => {
      toast.success(title, {
        description: description
      })
    }
  }
} 