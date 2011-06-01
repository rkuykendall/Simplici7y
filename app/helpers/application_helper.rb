# Methods added to this helper will be available to all templates in the application.
module ApplicationHelper
  def format(text)
    if text != nil
      text = Sanitize.clean(text)
      BlueCloth::new(text).to_html
    end
  end
  
  def clean(text)
    if text != nil
      text = Sanitize.clean(text)
    end
  end
  
end
