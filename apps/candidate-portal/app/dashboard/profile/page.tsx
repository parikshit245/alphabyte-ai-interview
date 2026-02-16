import { Button, Card, CardContent, CardDescription, CardHeader, CardTitle, Input, Label, Separator, Avatar, AvatarFallback, AvatarImage } from "@repo/ui";

export default function ProfilePage() {
  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Profile & Settings</h1>
        <p className="text-muted-foreground">Manage your account settings and preferences.</p>
      </div>
      <Separator />

      <Card>
        <CardHeader>
          <CardTitle>Personal Information</CardTitle>
          <CardDescription>Update your personal details.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center gap-6">
             <Avatar className="h-20 w-20">
               <AvatarImage src="" />
               <AvatarFallback className="text-lg">JD</AvatarFallback>
             </Avatar>
             <Button variant="outline">Change Avatar</Button>
          </div>
          
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="firstName">First name</Label>
              <Input id="firstName" placeholder="John" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="lastName">Last name</Label>
              <Input id="lastName" placeholder="Doe" />
            </div>
          </div>
          
          <div className="space-y-2">
             <Label htmlFor="email">Email</Label>
             <Input id="email" type="email" placeholder="john.doe@example.com" />
          </div>

          <div className="space-y-2">
             <Label htmlFor="bio">Bio</Label>
             <Input id="bio" placeholder="Tell us about yourself" />
          </div>
        </CardContent>
        <div className="flex items-center justify-end p-6 pt-0">
           <Button>Save Changes</Button>
        </div>
      </Card>
    </div>
  );
}
