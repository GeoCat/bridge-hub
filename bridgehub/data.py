from .servers import server_from_name

def layers(project, server):
	instance = server_from_name(server)
	instance.set_project_name(project)
	return instance.layers()